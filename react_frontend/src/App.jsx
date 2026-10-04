import { useCallback, useEffect, useState } from "react";

const blankForm = { barcode: "", product_name: "", brands: "", ingredients_text: "" };
const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5555";

async function request(path, options) {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(body?.Error || body?.error || `Request failed (${response.status})`);
  }
  return body;
}

function fromItem(item) {
  return {
    barcode: item.barcode ?? "",
    product_name: item.product?.product_name ?? "",
    brands: item.product?.brands ?? "",
    ingredients_text: item.product?.ingredients_text ?? "",
  };
}

export default function App() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState(blankForm);
  const [editingId, setEditingId] = useState(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const loadItems = useCallback(async () => {
    setBusy(true);
    setError("");
    try {
      setItems(await request("/inventory"));
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }, []);

  useEffect(() => {
    loadItems();
  }, [loadItems]);

  function changeField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
  }

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setMessage("");
    const payload = {
      barcode: form.barcode,
      product: {
        product_name: form.product_name,
        brands: form.brands,
        ingredients_text: form.ingredients_text,
      },
    };
    try {
      if (editingId === null) {
        const created = await request("/inventory", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setMessage(`Created item #${created.id}.`);
      } else {
        await request(`/inventory/${editingId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
        setMessage(`Updated item #${editingId}.`);
      }
      setForm(blankForm);
      setEditingId(null);
      await loadItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  function edit(item) {
    setEditingId(item.id);
    setForm(fromItem(item));
    setMessage("");
    setError("");
  }

  async function remove(item) {
    if (!window.confirm(`Delete ${item.product?.product_name || `item #${item.id}`}?`)) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await request(`/inventory/${item.id}`, { method: "DELETE" });
      setMessage(`Deleted item #${item.id}.`);
      if (editingId === item.id) {
        setEditingId(null);
        setForm(blankForm);
      }
      await loadItems();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function findById() {
    const id = window.prompt("Enter inventory ID:");
    if (!id) return;
    setError("");
    setMessage("");
    try {
      const item = await request(`/inventory/${encodeURIComponent(id)}`);
      setMessage(`GET /inventory/${id}: ${item.product?.product_name || "Item found"} (barcode ${item.barcode}).`);
    } catch (err) {
      setError(err.message);
    }
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(blankForm);
    setError("");
    setMessage("");
  }

  return (
    <main className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">FLASK API TESTER</p>
          <h1>Inventory</h1>
          <p className="subhead">Create, inspect, update, and delete inventory records.</p>
        </div>
        <button className="button secondary" onClick={findById} disabled={busy}>Find by ID</button>
      </header>

      {error && <div className="notice error" role="alert">{error}</div>}
      {message && <div className="notice success" role="status">{message}</div>}

      <section className="panel">
        <div className="section-heading">
          <div>
            <p className="eyebrow">{editingId === null ? "NEW RECORD" : `EDITING ITEM #${editingId}`}</p>
            <h2>{editingId === null ? "Add inventory item" : "Update inventory item"}</h2>
          </div>
          {editingId !== null && <button className="text-button" onClick={cancelEdit}>Cancel edit</button>}
        </div>
        <form onSubmit={submit}>
          <div className="fields">
            {[
              ["barcode", "Barcode"],
              ["product_name", "Product name"],
              ["brands", "Brand"],
              ["ingredients_text", "Ingredients"],
            ].map(([name, label]) => (
              <label key={name} className={name === "ingredients_text" ? "wide" : ""}>
                {label}
                <input
                  name={name}
                  value={form[name]}
                  onChange={changeField}
                  required
                  placeholder={`Enter ${label.toLowerCase()}`}
                />
              </label>
            ))}
          </div>
          <button className="button primary" type="submit" disabled={busy}>
            {busy ? "Working..." : editingId === null ? "Create item (POST)" : "Save changes (PATCH)"}
          </button>
        </form>
      </section>

      <section className="inventory-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">GET /inventory</p>
            <h2>Saved items <span className="count">{items.length}</span></h2>
          </div>
          <button className="button secondary" onClick={loadItems} disabled={busy}>Refresh</button>
        </div>
        {busy && items.length === 0 ? <p className="empty">Loading inventory...</p> : items.length === 0 ? (
          <p className="empty">No inventory records yet. Create one above.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead><tr><th>ID</th><th>Product</th><th>Barcode</th><th>Brand</th><th>Actions</th></tr></thead>
              <tbody>
                {items.map((item) => (
                  <tr key={item.id}>
                    <td className="id-cell">#{item.id}</td>
                    <td>
                      <strong>{item.product?.product_name || "Unnamed product"}</strong>
                      <span className="ingredients">{item.product?.ingredients_text || "No ingredients listed"}</span>
                    </td>
                    <td>{item.barcode}</td>
                    <td>{item.product?.brands || "—"}</td>
                    <td className="actions">
                      <button className="text-button" onClick={() => edit(item)}>Edit</button>
                      <button className="text-button danger-text" onClick={() => remove(item)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
      <footer>Requests are sent to the Flask routes; newly created items receive an ID from the backend.</footer>
    </main>
  );
}

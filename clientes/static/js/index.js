const tableBody_clientes = document.getElementById('tableBody_clientes');

async function listaClientes() {
  try {
    // Usá la URL con barra final (como en urls.py)
    const response = await fetch('/clientes/ListaClientes');
    const data = await response.json();

    let content = '';
    data.clientes.forEach((cliente, index) => {
      content += `
        <tr>
          <td class="centered">${cliente.nombre ?? ''}</td>
          <td class="centered">${cliente.localidad ?? ''}</td>
          <td class="centered">${cliente.divisa ?? ''}</td>
        </tr>`;
    });

    tableBody_clientes.innerHTML = content;

    // Inicializa DataTable si está disponible
    if (window.DataTable) {
      new DataTable('#datatable-clientes');
    }
  } catch (ex) {
    console.error(ex);
    alert('Error cargando clientes');
  }
}

window.addEventListener('load', listaClientes);

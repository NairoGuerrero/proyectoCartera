const LeerInfoTodos = async () => {
    try {


        const response = await fetch('/filtro_contrato/');
        const data = await response.json();

        console.log(data)

    } catch (ex) {
        console.log(ex);
    }
};

window.addEventListener("load", async () => {
    await LeerInfoTodos();

});
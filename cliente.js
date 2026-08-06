function abrirModal(
    nota,
    ordem,
    medida,
    motivo,
    criado
) {
    document.getElementById("mNota").innerText = nota;
    document.getElementById("mOrdem").innerText = ordem;
    document.getElementById("mMedida").innerText = medida;
    document.getElementById("mMotivo").innerText = motivo;

    document.getElementById("nota_hidden").value = nota;
    document.getElementById("ordem_hidden").value = ordem;

    document.getElementById("regularizado").value = "SIM";

    atualizarAcao();

    document.getElementById("modal").style.display = "block";
}

function salvarTratativa() {

    const data = {
        nota: document.getElementById("nota_hidden").value,

        ordem: document.getElementById("ordem_hidden").value,

        resultado: {
            REGULARIZADO:
                document.getElementById("regularizado").value,

            ACAO:
                document.getElementById("acao").value,

            OBSERVACAO:
                document.getElementById("observacao").value
        }
    };


    fetch("/cliente/tratamento", {

    method: "POST",

    headers: {
        "Content-Type": "application/json"
    },

    body: JSON.stringify(data)

})
.then(response => {

    console.log("STATUS:", response.status);

    if (!response.ok) {
        throw new Error(`Erro HTTP ${response.status}`);
    }

    return response.json();

})
.then(result => {

    console.log("RESULTADO:", result);

    if (result.status === "ok") {

        mostrarMensagem(
            "Tratativa salva com sucesso!",
            "sucesso"
        );

        document.getElementById("regularizado").value = "SIM";
        document.getElementById("observacao").value = "";

        fecharModal();

        setTimeout(() => {
            location.reload();
        }, 3000);

    } else {

        mostrarMensagem(
            result.mensagem,
            "erro"
        );

        console.error(result.mensagem);
    }

})
.catch(err => {

    console.error("ERRO:", err);

    mostrarMensagem(
        "Erro ao salvar a tratativa.",
        "erro"
    );

});
}

window.onclick = function (event) {

    let modal = document.getElementById("modal");

    if (event.target == modal) {
        modal.style.display = "none";
    }
};

function fecharModal() {

    document.getElementById("modal").style.display = "none";

    document.getElementById("observacao").value = "";
    document.getElementById("regularizado").value = "SIM";

    atualizarAcao();
}

document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {
        fecharModal();
    }
});

function atualizarAcao() {

    const reg = document.getElementById("regularizado").value;
    const acao = document.getElementById("acao");

    if (reg === "SIM") {
        acao.value = "FECHAR MEDIDA";
    } else {
        acao.value = "CANCELAR";
    }
}

function mostrarMensagem(texto, tipo) {

    const msg = document.getElementById("mensagem");

    msg.textContent = texto;
    msg.className = "msg " + tipo;

    msg.style.display = "block";

    setTimeout(() => {
        msg.classList.add("show");
    }, 10);

    setTimeout(() => {

        msg.classList.remove("show");

        setTimeout(() => {
            msg.style.display = "none";
        }, 300);

    }, 3000);
}

function filtrarNotas() {

    let filtro = document
        .getElementById("pesquisaNota")
        .value
        .toUpperCase();

    let tabela =
        document.getElementById("tabelaNotas");

    let linhas =
        tabela.getElementsByTagName("tr");

    for (let i = 1; i < linhas.length; i++) {

        let coluna =
            linhas[i].getElementsByTagName("td")[0];

        if (coluna) {

            let texto =
                coluna.textContent ||
                coluna.innerText;

            if (
                texto
                    .toUpperCase()
                    .indexOf(filtro) > -1
            ) {
                linhas[i].style.display = "";
            } else {
                linhas[i].style.display = "none";
            }
        }
    }
}

function toggleMenu() {

    document
        .getElementById("sidebar")
        .classList
        .toggle("hide");
}
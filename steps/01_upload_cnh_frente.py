import * as wmill from "windmill-client"
export async function main() {
  const urls = await wmill.getResumeUrls();

  return {
    title: "Como tirar a foto da CNH",
    description: [
      "Antes de enviar a imagem da frente da CNH, siga estas orientações:",
      "- Coloque o documento sobre uma superfície plana e bem iluminada",
      "- Evite reflexos ou sombras",
      "- Certifique-se de que todos os dados estejam legíveis",
      "- Use uma boa resolução (preferencialmente com o celular na horizontal)",
      "",
      "Quando estiver pronto, clique em **resume** para enviar a imagem."
    ].join("\n"),
    resume: urls.resume,
    cancel: urls.cancel
  };
}
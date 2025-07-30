import * as wmill from "windmill-client";

export async function main() {
  const urls = await wmill.getResumeUrls();

  return {
    description:
      "Como tirar a foto do QR Code (verso da CNH)\n\n" +
      "Antes de enviar a imagem do verso da CNH, siga estas orientações:\n" +
      "- Coloque o documento sobre uma superfície plana e bem iluminada\n" +
      "- Verifique se o QR Code está totalmente visível\n" +
      "- Evite reflexos, sombras ou cortes\n" +
      "- Utilize uma câmera com boa qualidade e foco\n\n" +
      "Quando estiver pronto, clique em 'Resume' para enviar a imagem.",
    resume: urls.resume,
    cancel: urls.cancel
  };
}

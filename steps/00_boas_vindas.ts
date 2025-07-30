import * as wmill from "windmill-client";

export async function main() {
  const urls = await wmill.getResumeUrls();

  return {
    description:
      "Bem-vindo ao Validador de CNH - mostQI Connect\n\n" +
      "Este fluxo irá conduzir você pelas etapas de validação automatizada da sua CNH, utilizando as APIs da mostQI.\n\n" +
      "Você precisará fornecer:\n" +
      "- Imagem da frente da CNH\n" +
      "- Imagem do verso com QR Code\n" +
      "- Vídeo para verificação de vivacidade\n\n" +
      "Para iniciar o processo, clique em Resume.\n" +
      "Para cancelar, clique em Cancel.",
    resume: urls.resume,
    cancel: urls.cancel
  };
}

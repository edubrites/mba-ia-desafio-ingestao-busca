from search import search_prompt

import sys


def main():
    try:
        chain = search_prompt()

        if not chain:
            print("❌ Não foi possível iniciar o chat. Verifique os erros de inicialização.")
            sys.exit(1)

        print("✅ Sistema RAG inicializado com sucesso!")
        print("Digite 'sair' para encerrar.\n")

        while True:
            try:
                pergunta = input("Faça sua pergunta: ").strip()

                if not pergunta:
                    continue

                if pergunta.lower() == 'sair':
                    print("\n👋 Encerrando...")
                    break

                print(f"\nPERGUNTA: {pergunta}")
                resposta = chain.invoke(pergunta)
                print(f"RESPOSTA: {resposta}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Encerrando...")
                break
            except Exception as e:
                print(f"❌ Erro ao processar pergunta: {e}\n")

    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

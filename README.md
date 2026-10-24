# Guarda Belo

<img src= "https://media1.tenor.com/m/2NM5Uc6A3kkAAAAC/ranger-smith-wink.gif" width="200">

Serviço para monitoramento de servidores Linux 🐧!

Atualmente ele conta com a função de informar login e logout de máquinas.

---

## Dependências:

- Python3.14
- wtmpdb

## Instalação

1. Crie um ambiente virtual com o python em sua máquina, pode ser usando o comando:

    ```bash
    $ python3 -m venv venv
    ```

2. Ative o ambiente virtual e instale os pacotes:

    ```bash
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    ```

3. Altere as variáveis de ambiente do arquivo **template.env** e mude o nome dele para `.env`.
4. Altere o arquivo de **guarda-belo.service** para que as variáveis `User`, `WorkingDirectory`, `EnvironmentFile` e `ExecStart` fiquem de acordo com as configurações do seu ambiente.
5. Crie um link simbólico do arquivo de serviço para a pasta de configurações do _Systemd_:

    ```bash
    $ sudo ln -s $PWD/guarda-belo.service /etc/systemd/system/guarda-belo.service
    ```
6. Reinicie o _Daemon_ do _Systemd_ para que ele identifique o novo serviço:

    ```bash
    $ sudo systemctl  daemon-reaload
    ```
7. Inicie o serviço de monitoramento:

    ```bash
    $ sudo systemctl start guarda-belo.service
    ```
8. Verifique se o serviço está executando corretamente:

    ```bash
    $ sudo systemctl status guarda-belo.service
    ```

Ele irá mandar o útimo login ou logout do servidor quando inicar o processo, mas irá monitorar para informar novos login/logout de um em um minuto!

## Executar na AWS (Cloud9 ou Code Server)

![image](https://user-images.githubusercontent.com/276077/162766448-13e0ebe8-8325-4e32-a8d7-5deff7744c10.png)

> Crie um ambiente no Cloud9 utilizando a instância `m5.large (8 GiB RAM + 2 vCPU)`.
> Se estiver usando o **Code server**, basta usar o ambiente já instalado. 

1. Baixe o projeto pub-sub para o Cloud9/Code Server.

```
wget https://github.com/rodrigoclira/pub-sub-kafka/archive/refs/heads/main.zip
```

3. Descompacte o arquivo zip

```
unzip main.zip
```

2. Modifique a porta na qual a aplicação (upload) vai rodar. No `docker-compose`, mude a seguinte parte: 

**antigo**
```
  upload:
    build: upload-app
    container_name: upload
    ports:
      - 5000:5000
```

**novo** 
```
  upload:
    build: upload-app
    container_name: upload
    ports:
      - 8080:5000
```

> Por que essa mudança foi necessária? Essa mudança é muito importante no Cloud9 pois ele automaticamente redireciona a porta 8080 para a porta 80 (preview)


4. Inicialize a composição com o comando abaixo:

```
sudo docker compose up --build
```

3. Acesse a página da aplicação através do botão de `Preview` do Cloud9. Se você estiver usando o Code Server, utilize apenas `https://IP-PUBLICO/proxy/8080/` para acessar o serviço de upload.


4. Espere o fim da inicialização (quando os logs pararem de atualizar de forma frenética) e visualize a comunicação assíncrona acontecendo.

5. No final, o arquivo que foi enviado para upload e suas versões rotacionadas e em preto e branco, estarão disponíveis na pasta `./appdata/`


-------
## Executar na AWS (EC2)

Realize esse passo a passo, caso você esteja utilizando o EC2 sem o Cloud9 ou Code Server instalado

* Utilize a instância do tipo `t2.medium`

![image](https://user-images.githubusercontent.com/276077/162766448-13e0ebe8-8325-4e32-a8d7-5deff7744c10.png)


1. Instalação de pacotes
```
sudo apt-get update
sudo apt-get install docker-compose unzip nginx -y
```


2. Download do repositório
```
wget  https://github.com/rodrigoclira/pub-sub-kafka/archive/refs/heads/main.zip
```

3. Descompactar repositório
```
unzip main.zip
```

4. Acessar pasta do repositório
```
cd devweb2-main/arquitetura/pub-sub
```

5. Removendo configuração anterior
```
sudo rm /etc/nginx/sites-enabled/default
```

6. Crie a pasta compartilhada
```
sudo mkdir -p /var/www/shared
sudo chmod -R 755 /var/www/shared
```

7. Copiando a configuração do proxy para a pasta do Nginx. O proxy é necessário uma vez que na rede do IFPE não é permitido acessar todas as portas do projeto
```
sudo cp server-config/pub_sub /etc/nginx/sites-enabled/ -v
```

8. Restartando o nginx
```
sudo systemctl restart nginx
```

9. Inicialize a composição
```
sudo docker-compose up --build
```

10. Acesse `http://PUBLIC-DNS/upload`

![image](https://github.com/user-attachments/assets/0a98eb67-4195-48f8-bbd9-2440f06abe3a)

Analise o log após enviar a imagem no `upload`. 
Para visualizar os dados processados, copie-os para a pasta compartilhada na web.

11. Copiando dados para visualizar em `http://PUBLIC-DNS/shared/`
```
sudo cp /home/ubuntu/devweb2-main/arquitetura/pub-sub/appdata/static/uploads/* /var/www/shared/ -R
```


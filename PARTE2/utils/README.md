O package *utils* contém scripts que tornam a codificação dos equipamentos mais simples. ```config.py``` contém as principais constantes do projeto, como o endereço de multicast, a porta multicast e o endereço e porta do servidor TCP do gateway.

```equipmentClass.py``` contém a definição da classe Equipment, que modela como um equipamento deve ser, basicamente. Os principais métodos, comuns a todos os equipamentos são:

1. **send_identification**(): Essa função serve para enviar a identificação do equipamento, com tipo, nome, ip e porta. Ao definir os elementos, novas variaveis podem ser utilizadas.

2. **send_msgn_TCP**(): Responsável por enviar uma mensagem definida com protocol buffers no aquivo .proto.

3. **setup_server**():  Essa função configura o servidor TCP de alguns equipamentos para comunicação com o Gateway.
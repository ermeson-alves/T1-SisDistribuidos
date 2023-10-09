Arquivos baixados em: https://github.com/protocolbuffers/protobuf/releases/tag/v24.4

1. ```protoc -I . --python_out . smart_house.proto``` serve para compilar o arquivo .proto que define as menssagens dos equipamentos. 

2. No linux x86_64 é possível já extrair os códigos do protoc com:

```code
unzip protoc-24.4-linux-x86_64.zip
```

3. Se o diretório atual for ```T1-SisDistribuidos/PARTE2```, para compilar o arquivo .proto com o formato das mensagens no linux x86_64 pode ser usado: 
  ```code 
  ../PROTO/bin/protoc -I . --python_out . smart_house.proto
  ```
<br>

---

<br>
<br>
<br>

"Protocol Buffers - Google's data interchange format
Copyright 2008 Google Inc.
https://developers.google.com/protocol-buffers/
This package contains a precompiled binary version of the protocol buffer
compiler (protoc). This binary is intended for users who want to use Protocol
Buffers in languages other than C++ but do not want to compile protoc
themselves. To install, simply place this binary somewhere in your PATH.
If you intend to use the included well known types then don't forget to
copy the contents of the 'include' directory somewhere as well, for example
into '/usr/local/include/'.
Please refer to our official github site for more installation instructions:
  https://github.com/protocolbuffers/protobuf"

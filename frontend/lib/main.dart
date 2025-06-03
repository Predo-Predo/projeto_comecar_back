import 'package:flutter/material.dart';
import 'tela_de_produtos.dart'; // importa o arquivo correto

void main() {
  runApp(const MeuApp());
}

class MeuApp extends StatelessWidget {
  const MeuApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Projeto Começar Back',
      theme: ThemeData(
        primarySwatch: Colors.teal,
      ),
      home: const TelaDeProdutosPage(), // usa TelaDeProdutosPage (não TelaDeProdutos)
    );
  }
}

import 'package:flutter/material.dart';
import 'formulario_assinatura_empresa.dart';
import 'tela_de_produtos.dart';

void main() {
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'White Label App',
      theme: ThemeData(primarySwatch: Colors.teal),
      home: TelaDeProdutos(),
  ));
}

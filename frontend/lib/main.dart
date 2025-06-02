import 'package:flutter/material.dart';
import 'formulario_assinatura_empresa.dart';

void main() {
  runApp(
    MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Cadastro de Empresas',
      theme: ThemeData(primarySwatch: Colors.teal),
      home: FormularioAssinaturaEmpresaPage(),
    ),
  );
}

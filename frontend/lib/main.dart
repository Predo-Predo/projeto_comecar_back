// lib/main.dart

import 'package:flutter/material.dart';
import 'login.dart';
import 'tela_de_produtos.dart';

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
      // Começa na tela de login
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginPage(),
        '/home': (context)  => const TelaDeProdutosPage(),
      },
    );
  }
}

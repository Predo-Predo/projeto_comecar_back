// lib/tela_de_produtos.dart

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'login.dart';                       // <<<<<<<<<<<<<<
import 'formulario_assinatura_empresa.dart';

class TelaDeProdutosPage extends StatefulWidget {
  const TelaDeProdutosPage({Key? key}) : super(key: key);

  @override
  State<TelaDeProdutosPage> createState() => _TelaDeProdutosPageState();
}

class _TelaDeProdutosPageState extends State<TelaDeProdutosPage> {
  final _storage = FlutterSecureStorage();
  late Future<List<Map<String, dynamic>>> _futureProjetos;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _verificaLogin();
    });
    _futureProjetos = _fetchProjetos();
  }

  Future<void> _verificaLogin() async {
    final token = await _storage.read(key: 'token');
    if (token == null || token.isEmpty) {
      // <<<<<<< navega diretamente para LoginPage
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => LoginPage()),
        (route) => false,
      );
    }
  }

  Future<List<Map<String, dynamic>>> _fetchProjetos() async {
    final resp = await http.get(Uri.parse('http://127.0.0.1:8000/projetos/'));
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as List;
      return data.map((p) => {
            'id': p['id'],
            'nome': p['nome'],
            'descricao': p['descricao'] ?? '',
          }).toList();
    }
    throw Exception('Falha ao carregar projetos: ${resp.statusCode}');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      appBar: AppBar(
        title: const Text('Escolha um Projeto'),
        backgroundColor: Colors.teal,
        centerTitle: true,
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _futureProjetos,
        builder: (ctx, snap) {
          if (snap.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snap.hasError) {
            return Center(child: Text('Erro: ${snap.error}'));
          } else if (snap.data == null || snap.data!.isEmpty) {
            return const Center(child: Text('Nenhum projeto encontrado.'));
          }
          final projetos = snap.data!;
          return ListView.builder(
            padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
            itemCount: projetos.length,
            itemBuilder: (ctx, i) {
              final projeto = projetos[i];
              return Card(
                elevation: 4,
                margin: const EdgeInsets.only(bottom: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        projeto['nome'],
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if ((projeto['descricao'] as String).isNotEmpty) ...[
                        const SizedBox(height: 8),
                        Text(
                          projeto['descricao'],
                          style: const TextStyle(fontSize: 14),
                        ),
                      ],
                      const SizedBox(height: 12),
                      ElevatedButton(
                        onPressed: () async {
                          final token = await _storage.read(key: 'token');
                          if (token == null || token.isEmpty) {
                            // redireciona direto para LoginPage
                            Navigator.of(context).pushAndRemoveUntil(
                              MaterialPageRoute(builder: (_) => LoginPage()),
                              (route) => false,
                            );
                            return;
                          }
                          await _storage.write(
                              key: 'empresaId',
                              value: projeto['id'].toString());
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => FormularioAssinaturaEmpresaPage(
                                  projetoId: projeto['id']),
                            ),
                          );
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.teal,
                          padding:
                              const EdgeInsets.symmetric(vertical: 12),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: const Text(
                          'Selecionar Projeto',
                          style: TextStyle(fontSize: 16),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}

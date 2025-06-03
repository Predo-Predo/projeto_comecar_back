// lib/tela_de_produtos.dart

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'formulario_assinatura_empresa.dart';

class TelaDeProdutosPage extends StatefulWidget {
  const TelaDeProdutosPage({Key? key}) : super(key: key);

  @override
  State<TelaDeProdutosPage> createState() => _TelaDeProdutosPageState();
}

class _TelaDeProdutosPageState extends State<TelaDeProdutosPage> {
  late Future<List<Map<String, dynamic>>> _futureProjetos;

  @override
  void initState() {
    super.initState();
    _futureProjetos = _fetchProjetos();
  }

  Future<List<Map<String, dynamic>>> _fetchProjetos() async {
    final response = await http.get(Uri.parse('http://127.0.0.1:8000/projetos/'));
    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data
          .map<Map<String, dynamic>>((p) => {
                'id': p['id'],
                'nome': p['nome'],
                'descricao': p['descricao'] ?? '',
              })
          .toList();
    } else {
      throw Exception('Falha ao carregar projetos: ${response.statusCode}');
    }
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
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Erro: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Nenhum projeto encontrado.'));
          } else {
            final projetos = snapshot.data!;
            return ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
              itemCount: projetos.length,
              itemBuilder: (context, index) {
                final projeto = projetos[index];
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
                          onPressed: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => FormularioAssinaturaEmpresaPage(
                                  projetoId: projeto['id'],
                                ),
                              ),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.teal,
                            padding: const EdgeInsets.symmetric(vertical: 12),
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
          }
        },
      ),
    );
  }
}

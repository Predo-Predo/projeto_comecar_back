// frontend/lib/selecao_de_empresa.dart

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

import 'formulario_app_empresa.dart';

class SelecaoDeEmpresaPage extends StatefulWidget {
  final int projetoId;

  const SelecaoDeEmpresaPage({Key? key, required this.projetoId}) : super(key: key);

  @override
  State<SelecaoDeEmpresaPage> createState() => _SelecaoDeEmpresaPageState();
}

class _SelecaoDeEmpresaPageState extends State<SelecaoDeEmpresaPage> {
  late Future<List<Map<String, dynamic>>> _futureEmpresas;
  final _secureStorage = FlutterSecureStorage();

  @override
  void initState() {
    super.initState();
    _futureEmpresas = _fetchEmpresas();
  }

  Future<List<Map<String, dynamic>>> _fetchEmpresas() async {
    final token = await _secureStorage.read(key: 'token');
    if (token == null) throw Exception('Token não encontrado');

    final response = await http.get(
      Uri.parse('http://127.0.0.1:8000/empresas/'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data
          .map<Map<String, dynamic>>((e) => {
                'id': e['id'],
                'nome': e['nome'],
                'cnpj': e['cnpj'],
              })
          .toList();
    } else {
      throw Exception('Falha ao carregar empresas: ${response.statusCode}');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      appBar: AppBar(
        title: const Text('Selecione uma Empresa'),
        backgroundColor: Colors.teal,
        centerTitle: true,
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _futureEmpresas,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Erro: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Nenhuma empresa encontrada.'));
          } else {
            final empresas = snapshot.data!;
            return ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
              itemCount: empresas.length,
              itemBuilder: (context, index) {
                final empresa = empresas[index];
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
                          empresa['nome'],
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'CNPJ: ${empresa['cnpj']}',
                          style: const TextStyle(fontSize: 14),
                        ),
                        const SizedBox(height: 12),
                        ElevatedButton(
                          onPressed: () {
                            Navigator.of(context).push(
                              MaterialPageRoute(
                                builder: (_) => FormularioAppEmpresaPage(
                                  empresaId: empresa['id'],
                                  projetoId: widget.projetoId,
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
                            'Selecionar Empresa',
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

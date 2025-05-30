import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ListaEmpresasPage extends StatefulWidget {
  @override
  _ListaEmpresasPageState createState() => _ListaEmpresasPageState();
}

class _ListaEmpresasPageState extends State<ListaEmpresasPage> {
  late Future<List<dynamic>> _futureEmpresas;

  @override
  void initState() {
    super.initState();
    _futureEmpresas = fetchEmpresas();
  }

  Future<List<dynamic>> fetchEmpresas() async {
    final response = await http.get(
      Uri.parse('http://127.0.0.1:8000/empresas/'),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('Falha ao carregar empresas');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Empresas Cadastradas')),
      body: FutureBuilder<List<dynamic>>(
        future: _futureEmpresas,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('Erro: ${snapshot.error}'));
          }
          final empresas = snapshot.data!;
          return ListView.separated(
            itemCount: empresas.length,
            separatorBuilder: (_, __) => Divider(),
            itemBuilder: (_, i) {
              final e = empresas[i];
              return ListTile(
                title: Text(e['name']),
                subtitle: Text(e['cnpj']),
                trailing: Text('#${e['id']}'),
              );
            },
          );
        },
      ),
    );
  }
}

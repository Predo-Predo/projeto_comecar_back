import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class FormularioAppEmpresaPage extends StatefulWidget {
  final int empresaId;
  const FormularioAppEmpresaPage({Key? key, required this.empresaId})
      : super(key: key);

  @override
  _FormularioAppEmpresaPageState createState() =>
      _FormularioAppEmpresaPageState();
}

class _FormularioAppEmpresaPageState extends State<FormularioAppEmpresaPage> {
  final _formKey = GlobalKey<FormState>();
  final _logoCtrl = TextEditingController();
  final _googleJsonCtrl = TextEditingController();
  final _appleTeamCtrl = TextEditingController();
  final _appleKeyCtrl = TextEditingController();
  final _appleIssuerCtrl = TextEditingController();
  int? _templateSelecionadoId;

  bool _submetendo = false;

  final List<Map<String, dynamic>> _templates = [
    {"id": 1, "nome": "Delivery"},
    {"id": 2, "nome": "Financeiro"},
  ];

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submetendo = true);

    final body = {
      "empresa_id": widget.empresaId,
      "logo_url": _logoCtrl.text.trim(),
      "google_service_json": jsonDecode(_googleJsonCtrl.text.trim()),
      "apple_team_id": _appleTeamCtrl.text.trim(),
      "apple_key_id": _appleKeyCtrl.text.trim(),
      "apple_issuer_id": _appleIssuerCtrl.text.trim(),
      "template_id": _templateSelecionadoId
    };

    final resp = await http.post(
      Uri.parse('http://127.0.0.1:8000/apps/'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );

    setState(() => _submetendo = false);

    if (resp.statusCode == 201) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Aplicativo criado com sucesso!')),
      );
      Navigator.of(context).pop();
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao criar app: ${resp.body}'),
          backgroundColor: Colors.redAccent,
        ),
      );
    }
  }

  @override
  void dispose() {
    _logoCtrl.dispose();
    _googleJsonCtrl.dispose();
    _appleTeamCtrl.dispose();
    _appleKeyCtrl.dispose();
    _appleIssuerCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      appBar: AppBar(
        title: Text('Configurar Aplicativo'),
        centerTitle: true,
        backgroundColor: Colors.teal,
        elevation: 0,
      ),
      body: Center(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24),
          child: Card(
            elevation: 6,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: EdgeInsets.all(24),
              child: Form(
                key: _formKey,
                child: Column(mainAxisSize: MainAxisSize.min, children: [
                  _buildField(controller: _logoCtrl, label: 'Logo (URL)'),
                  SizedBox(height: 16),
                  DropdownButtonFormField<int>(
                    value: _templateSelecionadoId,
                    decoration: InputDecoration(
                      labelText: 'Template do App',
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8)),
                    ),
                    items: _templates.map((template) {
                      return DropdownMenuItem<int>(
                        value: template['id'],
                        child: Text(template['nome']),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() {
                        _templateSelecionadoId = value;
                      });
                    },
                    validator: (value) =>
                        value == null ? 'Selecione um template' : null,
                  ),
                  SizedBox(height: 16),
                  TextFormField(
                    controller: _googleJsonCtrl,
                    decoration: InputDecoration(
                      labelText: 'Google Service JSON',
                      border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8)),
                    ),
                    maxLines: 3,
                    validator: (v) =>
                        v == null || v.trim().isEmpty ? 'Obrigatório' : null,
                  ),
                  SizedBox(height: 16),
                  _buildField(
                      controller: _appleTeamCtrl, label: 'Apple Team ID'),
                  SizedBox(height: 16),
                  _buildField(
                      controller: _appleKeyCtrl, label: 'Apple Key ID'),
                  SizedBox(height: 16),
                  _buildField(
                      controller: _appleIssuerCtrl, label: 'Apple Issuer ID'),
                  SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _submetendo ? null : _enviar,
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: Colors.teal,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: _submetendo
                          ? CircularProgressIndicator(color: Colors.white)
                          : Text('Cadastrar App',
                              style: TextStyle(fontSize: 16)),
                    ),
                  ),
                ]),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildField({
    required TextEditingController controller,
    required String label,
    TextInputType keyboardType = TextInputType.text,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      decoration: InputDecoration(
        labelText: label,
        border:
            OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: BorderSide(color: Colors.teal),
        ),
      ),
      validator: (v) =>
          v == null || v.trim().isEmpty ? 'Preencha este campo' : null,
    );
  }
}

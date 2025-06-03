import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'formulario_app_empresa.dart';

class FormularioAssinaturaEmpresaPage extends StatefulWidget {
  @override
  _FormularioAssinaturaEmpresaPageState createState() =>
      _FormularioAssinaturaEmpresaPageState();
}

class _FormularioAssinaturaEmpresaPageState
    extends State<FormularioAssinaturaEmpresaPage> {
  final _formKey = GlobalKey<FormState>();
  final _nomeCtrl = TextEditingController();
  final _cnpjCtrl = TextEditingController();
  final _emailContatoCtrl = TextEditingController();
  final _telefoneCtrl = TextEditingController();
  final _logoUrlCtrl = TextEditingController();

  bool _submetendo = false;

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submetendo = true);

    final body = {
      "nome": _nomeCtrl.text.trim(),
      "cnpj": _cnpjCtrl.text.trim(),
      "email_contato": _emailContatoCtrl.text.trim(),
      "telefone": _telefoneCtrl.text.trim(),
      "logo_empresa_url": _logoUrlCtrl.text.trim(),
    };

    final resp = await http.post(
      Uri.parse('http://127.0.0.1:8000/empresas/'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );

    setState(() => _submetendo = false);

    if (resp.statusCode == 201) {
      final data = jsonDecode(resp.body);
      final int empresaId = data['id'];

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Empresa cadastrada com sucesso!')),
      );
      _formKey.currentState!.reset();

      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => FormularioAppEmpresaPage(empresaId: empresaId),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao cadastrar: ${resp.body}'),
          backgroundColor: Colors.redAccent,
        ),
      );
    }
  }

  @override
  void dispose() {
    _nomeCtrl.dispose();
    _cnpjCtrl.dispose();
    _emailContatoCtrl.dispose();
    _telefoneCtrl.dispose();
    _logoUrlCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      appBar: AppBar(
        title: Text('Cadastrar Empresa'),
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
                  _buildField(controller: _nomeCtrl, label: 'Nome da Empresa'),
                  SizedBox(height: 16),
                  _buildField(controller: _cnpjCtrl, label: 'CNPJ'),
                  SizedBox(height: 16),
                  _buildField(
                    controller: _emailContatoCtrl,
                    label: 'E-mail de Contato',
                    keyboardType: TextInputType.emailAddress,
                  ),
                  SizedBox(height: 16),
                  _buildField(
                    controller: _telefoneCtrl,
                    label: 'Telefone',
                    keyboardType: TextInputType.phone,
                  ),
                  SizedBox(height: 16),
                  _buildField(controller: _logoUrlCtrl, label: 'Logo (URL)'),
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
                          : Text('Cadastrar Empresa',
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

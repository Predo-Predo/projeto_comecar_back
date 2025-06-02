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
  final _nameCtrl = TextEditingController();
  final _cnpjCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _phoneCtrl = TextEditingController();
  final _logoCtrl = TextEditingController();

  bool _submitting = false;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submitting = true);

    final body = {
      "name": _nameCtrl.text.trim(),
      "cnpj": _cnpjCtrl.text.trim(),
      "email_contact": _emailCtrl.text.trim(),
      "phone": _phoneCtrl.text.trim(),
      "logo_url": _logoCtrl.text.trim(),
    };

    final resp = await http.post(
      Uri.parse('http://127.0.0.1:8000/empresas/'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode(body),
    );

    setState(() => _submitting = false);

    if (resp.statusCode == 201) {
      final data = jsonDecode(resp.body);
      final int companyId = data['id'];

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Empresa cadastrada! ID: $companyId')),
      );
      _formKey.currentState!.reset();

      // Navega para o formulário de App, passando o companyId
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => FormularioAppEmpresaPage(companyId: companyId),
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
    _nameCtrl.dispose();
    _cnpjCtrl.dispose();
    _emailCtrl.dispose();
    _phoneCtrl.dispose();
    _logoCtrl.dispose();
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
                  _buildField(controller: _nameCtrl, label: 'Nome'),
                  SizedBox(height: 16),
                  _buildField(controller: _cnpjCtrl, label: 'CNPJ'),
                  SizedBox(height: 16),
                  _buildField(
                    controller: _emailCtrl,
                    label: 'Email de Contato',
                    keyboardType: TextInputType.emailAddress,
                  ),
                  SizedBox(height: 16),
                  _buildField(
                    controller: _phoneCtrl,
                    label: 'Telefone',
                    keyboardType: TextInputType.phone,
                  ),
                  SizedBox(height: 16),
                  _buildField(controller: _logoCtrl, label: 'Logo URL'),
                  SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _submitting ? null : _submit,
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        backgroundColor: Colors.teal,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: _submitting
                          ? CircularProgressIndicator(color: Colors.white)
                          : Text('Cadastrar', style: TextStyle(fontSize: 16)),
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

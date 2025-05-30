import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class FormularioAssinaturaEmpresaPage extends StatefulWidget {
  @override
  _FormularioAssinaturaEmpresaPageState createState() => _FormularioAssinaturaEmpresaPageState();
}

class _FormularioAssinaturaEmpresaPageState extends State<FormularioAssinaturaEmpresaPage> {
  final _formKey = GlobalKey<FormState>();

  // Controllers para cada campo
  final TextEditingController _nameController = TextEditingController();
  final TextEditingController _cnpjController = TextEditingController();
  final TextEditingController _emailContactController = TextEditingController();
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _logoUrlController = TextEditingController();
  final TextEditingController _appKeyController = TextEditingController();
  final TextEditingController _bundleIdController = TextEditingController();
  final TextEditingController _packageNameController = TextEditingController();
  final TextEditingController _appleTeamIdController = TextEditingController();
  final TextEditingController _appleKeyIdController = TextEditingController();
  final TextEditingController _appleIssuerIdController = TextEditingController();
  final TextEditingController _googleServiceJsonController = TextEditingController();

  // Cores do tema
  final Color _primaryColor = Color(0xFF2ECC71);
  final Color _underlineColor = Colors.grey;

  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _cnpjController.dispose();
    _emailContactController.dispose();
    _phoneController.dispose();
    _logoUrlController.dispose();
    _appKeyController.dispose();
    _bundleIdController.dispose();
    _packageNameController.dispose();
    _appleTeamIdController.dispose();
    _appleKeyIdController.dispose();
    _appleIssuerIdController.dispose();
    _googleServiceJsonController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _primaryColor,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0),
              child: ConstrainedBox(
                constraints: BoxConstraints(maxWidth: 500),
                child: Container(
                  padding: EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 8,
                        offset: Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Form(
                    key: _formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        // Ícone de fechar
                        Align(
                          alignment: Alignment.topRight,
                          child: GestureDetector(
                            onTap: () => Navigator.of(context).pop(),
                            child: Icon(Icons.close, color: _underlineColor),
                          ),
                        ),
                        SizedBox(height: 24),

                        // Campos empilhados verticalmente
                        _buildUnderlineField(
                          controller: _nameController,
                          label: 'Name',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _cnpjController,
                          label: 'CNPJ',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _emailContactController,
                          label: 'Email de Contato',
                          keyboardType: TextInputType.emailAddress,
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _phoneController,
                          label: 'Telefone',
                          keyboardType: TextInputType.phone,
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _logoUrlController,
                          label: 'Logo URL',
                          keyboardType: TextInputType.url,
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _appKeyController,
                          label: 'App Key',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _bundleIdController,
                          label: 'Bundle ID',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _packageNameController,
                          label: 'Package Name',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _appleTeamIdController,
                          label: 'Apple Team ID',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _appleKeyIdController,
                          label: 'Apple Key ID',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _appleIssuerIdController,
                          label: 'Apple Issuer ID',
                        ),
                        SizedBox(height: 24),
                        _buildUnderlineField(
                          controller: _googleServiceJsonController,
                          label: 'Google Service JSON',
                          maxLines: 4,
                        ),
                        SizedBox(height: 32),

                        _isLoading
                            ? Center(child: CircularProgressIndicator())
                            : ElevatedButton(
                                onPressed: _submit,
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: _primaryColor,
                                  foregroundColor: Colors.white,
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(30),
                                  ),
                                  padding: EdgeInsets.symmetric(vertical: 14),
                                ),
                                child: Text(
                                  'Enviar',
                                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                                ),
                              ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildUnderlineField({
    required TextEditingController controller,
    required String label,
    TextInputType keyboardType = TextInputType.text,
    int maxLines = 1,
  }) {
    return TextFormField(
      controller: controller,
      keyboardType: keyboardType,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: _underlineColor),
        border: InputBorder.none,
        enabledBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: _underlineColor),
        ),
        focusedBorder: UnderlineInputBorder(
          borderSide: BorderSide(color: _primaryColor),
        ),
      ),
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Preencha \$label';
        }
        return null;
      },
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    final data = {
      'name': _nameController.text,
      'cnpj': _cnpjController.text,
      'email_contact': _emailContactController.text,
      'phone': _phoneController.text,
      'logo_url': _logoUrlController.text,
      'app_key': _appKeyController.text,
      'bundle_id': _bundleIdController.text,
      'package_name': _packageNameController.text,
      'apple_team_id': _appleTeamIdController.text,
      'apple_key_id': _appleKeyIdController.text,
      'apple_issuer_id': _appleIssuerIdController.text,
      'google_service_json': jsonDecode(_googleServiceJsonController.text),
    };

    final response = await http.post(
      Uri.parse('http://127.0.0.1:8000/empresas/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(data),
    );

    setState(() => _isLoading = false);

    if (response.statusCode == 201) {
      final created = jsonDecode(response.body);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Empresa criada com ID ${created['id']}')),
      );
      // Opcional: limpar campos
      _formKey.currentState!.reset();
    } else {
      final error = jsonDecode(response.body);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: ${error['detail'] ?? response.body}')),
      );
    }
  }
}

// lib/formulario_assinatura_empresa.dart

import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';            // para kIsWeb
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'formulario_app_empresa.dart';

class FormularioAssinaturaEmpresaPage extends StatefulWidget {
  final int projetoId;
  const FormularioAssinaturaEmpresaPage({
    Key? key,
    required this.projetoId,
  }) : super(key: key);

  @override
  _FormularioAssinaturaEmpresaPageState createState() =>
      _FormularioAssinaturaEmpresaPageState();
}

class _FormularioAssinaturaEmpresaPageState
    extends State<FormularioAssinaturaEmpresaPage> {
  // **Use a mesma URL do seu login.dart**
  static const String BACKEND_URL =
      'https://3213-177-129-251-249.ngrok-free.app';

  final _formKey = GlobalKey<FormState>();
  final _nomeCtrl = TextEditingController();
  final _cnpjCtrl = TextEditingController();
  final _emailContatoCtrl = TextEditingController();
  final _telefoneCtrl = TextEditingController();

  PlatformFile? _pickedFile;
  bool _submetendo = false;

  Future<void> _pickLogo() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      withData: kIsWeb, // carrega bytes no Web
    );
    if (result != null && result.files.single.name.isNotEmpty) {
      setState(() => _pickedFile = result.files.single);
      debugPrint('🖼️ Arquivo selecionado: ${_pickedFile!.name}'
          ' (${_pickedFile!.size} bytes)');
    } else {
      debugPrint('🖼️ Nenhum arquivo selecionado.');
    }
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submetendo = true);

    final uri = Uri.parse('$BACKEND_URL/empresas/');
    final req = http.MultipartRequest('POST', uri);

    // Campos de texto
    req.fields['nome'] = _nomeCtrl.text.trim();
    req.fields['cnpj'] = _cnpjCtrl.text.trim();
    req.fields['email_contato'] = _emailContatoCtrl.text.trim();
    req.fields['telefone'] = _telefoneCtrl.text.trim();

    // Anexa o logo, se selecionado
    if (_pickedFile != null) {
      if (kIsWeb && _pickedFile!.bytes != null) {
        req.files.add(http.MultipartFile.fromBytes(
          'logo_empresa',
          _pickedFile!.bytes!,
          filename: _pickedFile!.name,
        ));
      } else if (_pickedFile!.path != null) {
        req.files.add(await http.MultipartFile.fromPath(
          'logo_empresa',
          _pickedFile!.path!,
        ));
      }
    }

    debugPrint('📤 Enviando requisição:'
        '\n • URI: $uri'
        '\n • fields: ${req.fields.keys.toList()}'
        '\n • files: ${req.files.map((f) => f.filename).toList()}');

    try {
      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);

      debugPrint('📥 Resposta do servidor: ${resp.statusCode} → ${resp.body}');

      if (resp.statusCode == 201) {
        final data = jsonDecode(resp.body);
        final int empresaId = data['id'];
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Empresa cadastrada com sucesso!')),
        );
        _formKey.currentState!.reset();
        setState(() => _pickedFile = null);

        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => FormularioAppEmpresaPage(
              empresaId: empresaId,
              projetoId: widget.projetoId,
            ),
          ),
        );
      } else {
        throw Exception('Falha (${resp.statusCode}): ${resp.body}');
      }
    } catch (e) {
      debugPrint('❌ Erro ao enviar: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Erro ao cadastrar: $e'),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      setState(() => _submetendo = false);
    }
  }

  @override
  void dispose() {
    _nomeCtrl.dispose();
    _cnpjCtrl.dispose();
    _emailContatoCtrl.dispose();
    _telefoneCtrl.dispose();
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

                  // Seletor de logo
                  GestureDetector(
                    onTap: _pickLogo,
                    child: Container(
                      height: 150,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: _pickedFile == null
                          ? Center(child: Text('Clique para escolher o logo'))
                          : ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: kIsWeb
                                  ? Image.memory(
                                      _pickedFile!.bytes!,
                                      fit: BoxFit.cover,
                                    )
                                  : Image.file(
                                      File(_pickedFile!.path!),
                                      fit: BoxFit.cover,
                                    ),
                            ),
                    ),
                  ),
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
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
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

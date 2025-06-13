import 'dart:io';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;

import 'formulario_app_empresa.dart';

class FormularioAppEmpresaPage extends StatefulWidget {
  final int empresaId;
  final int projetoId;

  const FormularioAppEmpresaPage({
    Key? key,
    required this.empresaId,
    required this.projetoId,
  }) : super(key: key);

  @override
  State<FormularioAppEmpresaPage> createState() =>
      _FormularioAppEmpresaPageState();
}

class _FormularioAppEmpresaPageState
    extends State<FormularioAppEmpresaPage> {
  final _formKey = GlobalKey<FormState>();
  File? _logoFile;
  final _googleJsonCtrl = TextEditingController();
  final _appleTeamCtrl   = TextEditingController();
  final _appleKeyCtrl    = TextEditingController();
  final _appleIssuerCtrl = TextEditingController();

  bool _submitting = false;

  Future<void> _submitApp() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _submitting = true);

    // Monta a requisição multipart
    final uri = Uri.parse('http://127.0.0.1:8000/apps/');
    final req = http.MultipartRequest('POST', uri)
      ..fields['empresa_id']          = widget.empresaId.toString()
      ..fields['google_service_json'] = _googleJsonCtrl.text.trim()
      ..fields['apple_team_id']       = _appleTeamCtrl.text.trim()
      ..fields['apple_key_id']        = _appleKeyCtrl.text.trim()
      ..fields['apple_issuer_id']     = _appleIssuerCtrl.text.trim()
      ..fields['projeto_id']          = widget.projetoId.toString();

    // Anexa o arquivo de logo
    if (_logoFile != null) {
      req.files.add(await http.MultipartFile.fromPath(
        'logo_app',      // deve bater com UploadFile = File(...) no backend
        _logoFile!.path,
      ));
    }

    // Envia e aguarda resposta
    final streamed = await req.send();
    final resp = await http.Response.fromStream(streamed);
    setState(() => _submitting = false);

    if (resp.statusCode == 201) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('App criado com sucesso!')),
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
        title: Text('Configurar App'),
        backgroundColor: Colors.teal,
        centerTitle: true,
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
                  // Seletor de logo do App
                  GestureDetector(
                    onTap: () async {
                      final result = await FilePicker.platform.pickFiles(
                        type: FileType.image,
                      );
                      if (result != null && result.files.single.path != null) {
                        setState(() {
                          _logoFile = File(result.files.single.path!);
                        });
                      }
                    },
                    child: Container(
                      height: 150,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: _logoFile == null
                          ? Center(child: Text('Clique para escolher o logo'))
                          : ClipRRect(
                              borderRadius: BorderRadius.circular(8),
                              child: Image.file(_logoFile!,
                                  fit: BoxFit.cover),
                            ),
                    ),
                  ),
                  SizedBox(height: 16),

                  // Google Service JSON
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

                  // Apple Team ID
                  _buildField(
                    controller: _appleTeamCtrl,
                    label: 'Apple Team ID',
                  ),
                  SizedBox(height: 16),

                  // Apple Key ID
                  _buildField(
                    controller: _appleKeyCtrl,
                    label: 'Apple Key ID',
                  ),
                  SizedBox(height: 16),

                  // Apple Issuer ID
                  _buildField(
                    controller: _appleIssuerCtrl,
                    label: 'Apple Issuer ID',
                  ),
                  SizedBox(height: 24),

                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _submitting ? null : _submitApp,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.teal,
                        padding: EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8)),
                      ),
                      child: _submitting
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

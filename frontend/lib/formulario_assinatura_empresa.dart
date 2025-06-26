// lib/formulario_assinatura_empresa.dart

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html;

class FormularioAssinaturaEmpresaPage extends StatefulWidget {
  final int projetoId;
  const FormularioAssinaturaEmpresaPage({Key? key, required this.projetoId}) : super(key: key);

  @override
  _FormularioAssinaturaEmpresaPageState createState() => _FormularioAssinaturaEmpresaPageState();
}

class _FormularioAssinaturaEmpresaPageState extends State<FormularioAssinaturaEmpresaPage> {
  static const String BACKEND_URL = 'https://c00b-177-129-251-249.ngrok-free.app';

  final _formKey = GlobalKey<FormState>();
  final _nomeCtrl = TextEditingController();
  final _cnpjCtrl = TextEditingController();
  final _emailContatoCtrl = TextEditingController();
  final _telefoneCtrl = TextEditingController();

  Uint8List? _logoBytes;
  String? _logoName;
  bool _submetendo = false;

  final _secureStorage = FlutterSecureStorage();

  Future<void> _pickLogo() async {
    if (kIsWeb) {
      final uploadInput = html.FileUploadInputElement()..accept = 'image/*';
      uploadInput.click();
      uploadInput.onChange.listen((event) {
        final file = uploadInput.files?.first;
        if (file == null) return;
        final reader = html.FileReader();
        reader.readAsArrayBuffer(file);
        reader.onLoadEnd.listen((_) {
          setState(() {
            _logoBytes = reader.result as Uint8List;
            _logoName = file.name;
          });
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Logo selecionado: ${file.name}')));
        });
      });
    } else {
      final XFile? picked = await ImagePicker().pickImage(source: ImageSource.gallery);
      if (picked == null) return;
      final bytes = await picked.readAsBytes();
      setState(() {
        _logoBytes = bytes;
        _logoName = picked.name;
      });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Logo selecionado: ${picked.name}')));
    }
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;

    if (_logoBytes == null || _logoName == null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Você precisa escolher um logo')));
      return;
    }

    setState(() => _submetendo = true);

    try {
      final token = await _secureStorage.read(key: 'token');

      if (token == null) {
        throw Exception('Usuário não autenticado');
      }

      final uri = Uri.parse('$BACKEND_URL/empresas/');
      final req = http.MultipartRequest('POST', uri)
        ..fields['nome'] = _nomeCtrl.text.trim()
        ..fields['cnpj'] = _cnpjCtrl.text.trim()
        ..fields['email_contato'] = _emailContatoCtrl.text.trim()
        ..fields['telefone'] = _telefoneCtrl.text.trim()
        ..headers.addAll({
          'Authorization': 'Bearer $token',
          'Content-Type': 'multipart/form-data; charset=utf-8',
        })
        ..files.add(http.MultipartFile.fromBytes(
          'logo_empresa',
          _logoBytes!,
          filename: _logoName!,
        ));

      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);

      if (resp.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Empresa cadastrada com sucesso!')));
        Navigator.of(context).pop(true); // <- retorna para tela anterior
      } else {
        throw Exception('Status ${resp.statusCode}: ${resp.body}');
      }
    } catch (e, stack) {
      print('Erro ao enviar: $e\nStack: $stack');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro ao cadastrar: $e'), backgroundColor: Colors.redAccent),
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
      appBar: AppBar(title: Text('Cadastrar Empresa'), backgroundColor: Colors.teal),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _buildField(_nomeCtrl, 'Nome da Empresa'),
              SizedBox(height: 16),
              _buildField(_cnpjCtrl, 'CNPJ'),
              SizedBox(height: 16),
              _buildField(_emailContatoCtrl, 'E-mail de Contato', TextInputType.emailAddress),
              SizedBox(height: 16),
              _buildField(_telefoneCtrl, 'Telefone', TextInputType.phone),
              SizedBox(height: 16),
              Column(
                children: [
                  ElevatedButton(
                    onPressed: _pickLogo,
                    child: Text('Selecionar Imagem.'),
                  ),
                  SizedBox(height: 16),
                  if (_logoBytes != null)
                    Container(
                      height: 150,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Image.memory(_logoBytes!, fit: BoxFit.cover),
                    )
                  else
                    Text('Nenhuma imagem selecionada ainda.'),
                ],
              ),
              if (_logoName != null) ...[
                SizedBox(height: 8),
                Text('Arquivo: $_logoName'),
              ],
              SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submetendo ? null : _enviar,
                  child: _submetendo
                      ? CircularProgressIndicator(color: Colors.white)
                      : Text('Cadastrar Empresa'),
                  style: ElevatedButton.styleFrom(
                    padding: EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: Colors.teal,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildField(TextEditingController ctrl, String label,
      [TextInputType type = TextInputType.text]) {
    return TextFormField(
      controller: ctrl,
      keyboardType: type,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(),
      ),
      validator: (v) =>
          v == null || v.trim().isEmpty ? 'Preencha este campo' : null,
    );
  }
}

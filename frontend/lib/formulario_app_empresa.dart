// frontend/lib/formulario_app_empresa.dart

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'dart:html' as html;

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

class _FormularioAppEmpresaPageState extends State<FormularioAppEmpresaPage> {
  static const String BACKEND_URL = 'http://127.0.0.1:8000';

  final _formKey = GlobalKey<FormState>();
  final _nomeAppCtrl = TextEditingController();
  final _descricaoCtrl = TextEditingController();

  Uint8List? _iconeBytes;
  String? _iconeNome;
  bool _submetendo = false;

  final _secureStorage = FlutterSecureStorage();

  Future<void> _pickIcon() async {
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
            _iconeBytes = reader.result as Uint8List;
            _iconeNome = file.name;
          });
          ScaffoldMessenger.of(context)
              .showSnackBar(SnackBar(content: Text('Ícone selecionado: ${file.name}')));
        });
      });
    } else {
      final XFile? picked = await ImagePicker().pickImage(source: ImageSource.gallery);
      if (picked == null) return;
      final bytes = await picked.readAsBytes();
      setState(() {
        _iconeBytes = bytes;
        _iconeNome = picked.name;
      });
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Ícone selecionado: ${picked.name}')));
    }
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;

    if (_iconeBytes == null || _iconeNome == null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Você precisa escolher um ícone')));
      return;
    }

    setState(() => _submetendo = true);

    try {
      final token = await _secureStorage.read(key: 'token');
      if (token == null) throw Exception('Usuário não autenticado');

      final uri = Uri.parse('$BACKEND_URL/apps/');
      final req = http.MultipartRequest('POST', uri)
        ..fields['empresa_id'] = widget.empresaId.toString()
        ..fields['projeto_id'] = widget.projetoId.toString()
        ..fields['nome'] = _nomeAppCtrl.text.trim()
        ..fields['descricao'] = _descricaoCtrl.text.trim()
        ..headers.addAll({
          'Authorization': 'Bearer $token',
          'Content-Type': 'multipart/form-data; charset=utf-8',
        })
        ..files.add(http.MultipartFile.fromBytes(
          'logo_app',
          _iconeBytes!,
          filename: _iconeNome!,
        ));

      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);

      if (resp.statusCode == 201) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('App cadastrado com sucesso!')));
        Navigator.of(context).pop();
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
    _nomeAppCtrl.dispose();
    _descricaoCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal.shade50,
      appBar: AppBar(title: Text('Configurar App'), backgroundColor: Colors.teal),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              _buildField(_nomeAppCtrl, 'Nome do App'),
              SizedBox(height: 16),
              _buildField(_descricaoCtrl, 'Descrição do App (sobre o app)', TextInputType.multiline, 3),
              SizedBox(height: 16),
              Column(
                children: [
                  ElevatedButton(
                    onPressed: _pickIcon,
                    child: Text('Selecionar Ícone'),
                  ),
                  SizedBox(height: 16),
                  if (_iconeBytes != null)
                    Container(
                      height: 150,
                      width: double.infinity,
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Image.memory(_iconeBytes!, fit: BoxFit.cover),
                    )
                  else
                    Text('Nenhum ícone selecionado ainda.'),
                ],
              ),
              if (_iconeNome != null) ...[
                SizedBox(height: 8),
                Text('Arquivo: $_iconeNome'),
              ],
              SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _submetendo ? null : _enviar,
                  child: _submetendo
                      ? CircularProgressIndicator(color: Colors.white)
                      : Text('Cadastrar App'),
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
      [TextInputType type = TextInputType.text, int maxLines = 1]) {
    return TextFormField(
      controller: ctrl,
      keyboardType: type,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(),
      ),
      validator: (v) =>
          v == null || v.trim().isEmpty ? 'Preencha este campo' : null,
    );
  }
}

// lib/formulario_assinatura_empresa.dart

import 'dart:convert';
import 'dart:html' as html;
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

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
  static const String BACKEND_URL =
      'https://3213-177-129-251-249.ngrok-free.app';

  final _formKey = GlobalKey<FormState>();
  final _nomeCtrl = TextEditingController();
  final _cnpjCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _telCtrl = TextEditingController();

  html.File? _webFile;
  Uint8List? _previewBytes;
  bool _carregando = false;

  void _pickLogo() {
    final uploadInput = html.FileUploadInputElement()
      ..accept = 'image/*'
      ..click();

    uploadInput.onChange.listen((event) {
      final files = uploadInput.files;
      if (files == null || files.isEmpty) return;
      final file = files.first;
      final reader = html.FileReader();
      reader.readAsArrayBuffer(file);
      reader.onLoadEnd.listen((e) {
        setState(() {
          _webFile = file;
          _previewBytes = reader.result as Uint8List;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Selecionado: ${file.name}')),
        );
      });
    });
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    if (_webFile == null || _previewBytes == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Você precisa escolher um logo')),
      );
      return;
    }

    setState(() => _carregando = true);

    final uri = Uri.parse('$BACKEND_URL/empresas/');
    final req = http.MultipartRequest('POST', uri)
      ..fields['nome'] = _nomeCtrl.text.trim()
      ..fields['cnpj'] = _cnpjCtrl.text.trim()
      ..fields['email_contato'] = _emailCtrl.text.trim()
      ..fields['telefone'] = _telCtrl.text.trim()
      ..files.add(http.MultipartFile.fromBytes(
        'logo_empresa',
        _previewBytes!,
        filename: _webFile!.name,
        contentType: MediaType(
          'image',
          _webFile!.type.split('/').last,
        ),
      ));

    try {
      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);
      if (resp.statusCode == 201) {
        final id = jsonDecode(resp.body)['id'] as int;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Empresa criada! id=$id')),
        );
        Navigator.of(context).pushReplacement(MaterialPageRoute(
          builder: (_) => FormularioAppEmpresaPage(
            empresaId: id,
            projetoId: widget.projetoId,
          ),
        ));
      } else {
        throw Exception('HTTP ${resp.statusCode}: ${resp.body}');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro: $e'), backgroundColor: Colors.red),
      );
    } finally {
      setState(() => _carregando = false);
    }
  }

  @override
  void dispose() {
    _nomeCtrl.dispose();
    _cnpjCtrl.dispose();
    _emailCtrl.dispose();
    _telCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Cadastrar Empresa')),
      backgroundColor: Colors.teal.shade50,
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(children: [
            _buildField(_nomeCtrl, 'Nome da Empresa'),
            SizedBox(height: 16),
            _buildField(_cnpjCtrl, 'CNPJ'),
            SizedBox(height: 16),
            _buildField(_emailCtrl, 'E-mail de Contato',
                TextInputType.emailAddress),
            SizedBox(height: 16),
            _buildField(_telCtrl, 'Telefone', TextInputType.phone),
            SizedBox(height: 24),
            GestureDetector(
              onTap: _pickLogo,
              child: Container(
                height: 150,
                width: double.infinity,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                  color: Colors.white,
                ),
                alignment: Alignment.center,
                child: _previewBytes == null
                    ? Text('Clique para escolher o logo')
                    : Image.memory(_previewBytes!, fit: BoxFit.cover),
              ),
            ),
            SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _carregando ? null : _enviar,
                style: ElevatedButton.styleFrom(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  backgroundColor: Colors.teal,
                ),
                child: _carregando
                    ? CircularProgressIndicator(color: Colors.white)
                    : Text('Cadastrar Empresa'),
              ),
            ),
          ]),
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

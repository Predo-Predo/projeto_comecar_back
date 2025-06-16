// lib/formulario_assinatura_empresa.dart

import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'formulario_app_empresa.dart';
import 'conditional_file.dart' if (dart.library.io) 'dart:io' show File;

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
  final _emailContatoCtrl = TextEditingController();
  final _telefoneCtrl = TextEditingController();

  PlatformFile? _pickedFile;
  bool _submetendo = false;

  Future<void> _pickLogo() async {
    print('[DEBUG] _pickLogo chamado');
    final result = await FilePicker.platform.pickFiles(
      // em vez de FileType.image, usamos custom para não depender do mapeamento interno
      type: FileType.custom,
      allowedExtensions: ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
      withData: true, // sempre carrega bytes
    );
    print('[DEBUG] pickFiles result: $result');
    if (result == null || result.files.isEmpty) {
      print('[DEBUG] nenhum arquivo selecionado');
      return;
    }
    final file = result.files.single;
    print(
      '[DEBUG] arquivo: name=${file.name} size=${file.size} bytesLength=${file.bytes?.length}'
    );
    setState(() => _pickedFile = file);
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    if (_pickedFile == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Você precisa escolher um logo')),
      );
      return;
    }

    setState(() => _submetendo = true);
    final uri = Uri.parse('$BACKEND_URL/empresas/');
    final req = http.MultipartRequest('POST', uri)
      ..fields['nome'] = _nomeCtrl.text.trim()
      ..fields['cnpj'] = _cnpjCtrl.text.trim()
      ..fields['email_contato'] = _emailContatoCtrl.text.trim()
      ..fields['telefone'] = _telefoneCtrl.text.trim()
      ..files.add(http.MultipartFile.fromBytes(
        'logo_empresa',
        _pickedFile!.bytes!,
        filename: _pickedFile!.name,
      ));

    try {
      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);
      if (resp.statusCode == 201) {
        final data = jsonDecode(resp.body);
        final empresaId = data['id'] as int;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Empresa cadastrada com sucesso!')),
        );
        Navigator.of(context).pushReplacement(MaterialPageRoute(
          builder: (_) => FormularioAppEmpresaPage(
            empresaId: empresaId,
            projetoId: widget.projetoId,
          ),
        ));
      } else {
        throw Exception('Status ${resp.statusCode}: ${resp.body}');
      }
    } catch (e) {
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
      appBar: AppBar(title: Text('Cadastrar Empresa'), backgroundColor: Colors.teal),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(children: [
            _buildField(_nomeCtrl, 'Nome da Empresa'),
            SizedBox(height: 16),
            _buildField(_cnpjCtrl, 'CNPJ'),
            SizedBox(height: 16),
            _buildField(_emailContatoCtrl, 'E-mail de Contato', TextInputType.emailAddress),
            SizedBox(height: 16),
            _buildField(_telefoneCtrl, 'Telefone', TextInputType.phone),
            SizedBox(height: 16),
            GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: _pickLogo,
              child: Container(
                height: 150,
                width: double.infinity,
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey),
                  borderRadius: BorderRadius.circular(8),
                ),
                clipBehavior: Clip.hardEdge,
                child: _pickedFile == null
                    ? Center(child: Text('Clique para escolher o logo'))
                    : _buildPreview(),
              ),
            ),
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
          ]),
        ),
      ),
    );
  }

  Widget _buildPreview() {
    final bytes = _pickedFile!.bytes;
    if (bytes != null) {
      return Image.memory(bytes, fit: BoxFit.cover, width: double.infinity, height: double.infinity);
    } else {
      return Image.file(
        File(_pickedFile!.path!),
        fit: BoxFit.cover,
        width: double.infinity,
        height: double.infinity,
      );
    }
  }

  Widget _buildField(
    TextEditingController ctrl,
    String label, [
    TextInputType type = TextInputType.text,
  ]) {
    return TextFormField(
      controller: ctrl,
      keyboardType: type,
      decoration: InputDecoration(labelText: label, border: OutlineInputBorder()),
      validator: (v) => v == null || v.trim().isEmpty ? 'Preencha este campo' : null,
    );
  }
}

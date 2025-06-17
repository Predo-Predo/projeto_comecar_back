// lib/formulario_assinatura_empresa.dart

import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'formulario_app_empresa.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:html' as html;

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

  Uint8List? _logoBytes;
  String? _logoName;
  bool _submetendo = false;

  Future<void> _pickLogo() async {
    print('==> _pickLogo chamado');
    if (kIsWeb) {
      print('Tentando selecionar arquivo na Web...');
      final uploadInput = html.FileUploadInputElement()..accept = 'image/*';
      uploadInput.click();

      uploadInput.onChange.listen((event) {
        final file = uploadInput.files?.first;
        if (file == null) {
          print('Nenhum arquivo selecionado');
          return;
        }

        final reader = html.FileReader();
        reader.readAsArrayBuffer(file);
        reader.onLoadEnd.listen((_) {
          setState(() {
            _logoBytes = reader.result as Uint8List;
            _logoName = file.name;
          });

          print('Arquivo selecionado: ${file.name}');
          print('Tamanho: ${_logoBytes?.length ?? 0} bytes');

          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Logo selecionado: ${file.name}')),
          );
        });
      });
    } else {
      print('Selecionando imagem em mobile/desktop...');
      final XFile? picked = await ImagePicker().pickImage(
        source: ImageSource.gallery,
        maxWidth: 1200,
        maxHeight: 1200,
        imageQuality: 90,
      );
      if (picked == null) {
        print('Nenhuma imagem selecionada');
        return;
      }

      final bytes = await picked.readAsBytes();
      setState(() {
        _logoBytes = bytes;
        _logoName = picked.name;
      });

      print('Imagem selecionada: ${picked.name}');
      print('Tamanho: ${bytes.length} bytes');

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Logo selecionado: ${picked.name}')),
      );
    }
  }

  Future<void> _enviar() async {
    print('===> Enviando dados...');
    print('Nome: ${_nomeCtrl.text}');
    print('CNPJ: ${_cnpjCtrl.text}');
    print('Email: ${_emailContatoCtrl.text}');
    print('Telefone: ${_telefoneCtrl.text}');
    print('Logo: $_logoName (${_logoBytes?.length ?? 0} bytes)');

    if (!_formKey.currentState!.validate()) {
      print('Formulário inválido');
      return;
    }

    if (_logoBytes == null || _logoName == null) {
      print('Logo não selecionado');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Você precisa escolher um logo')),
      );
      return;
    }

    setState(() => _submetendo = true);

    try {
      final uri = Uri.parse('$BACKEND_URL/empresas/');
      final req = http.MultipartRequest('POST', uri)
        ..fields['nome'] = _nomeCtrl.text.trim()
        ..fields['cnpj'] = _cnpjCtrl.text.trim()
        ..fields['email_contato'] = _emailContatoCtrl.text.trim()
        ..fields['telefone'] = _telefoneCtrl.text.trim()
        ..files.add(http.MultipartFile.fromBytes(
          'logo_empresa',
          _logoBytes!,
          filename: _logoName!,
        ));

      print('Enviando requisição POST...');
      final streamed = await req.send();
      final resp = await http.Response.fromStream(streamed);
      print('Status HTTP: ${resp.statusCode}');
      print('Resposta: ${resp.body}');

      if (resp.statusCode == 201) {
        final data = jsonDecode(resp.body);
        final empresaId = data['id'] as int;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Empresa cadastrada com sucesso!')),
        );
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => FormularioAppEmpresaPage(
              empresaId: empresaId,
              projetoId: widget.projetoId,
            ),
          ),
        );
      } else {
        throw Exception('Status ${resp.statusCode}: ${resp.body}');
      }
    } catch (e, stack) {
      print('Erro ao enviar: $e');
      print('Stack: $stack');
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
    print('Tela carregada!');
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
                      child: Image.memory(
                        _logoBytes!,
                        fit: BoxFit.cover,
                      ),
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

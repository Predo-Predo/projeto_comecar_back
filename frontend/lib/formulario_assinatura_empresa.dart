// lib/formulario_assinatura_empresa.dart

import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'formulario_app_empresa.dart';

// Import condicional: usa web_file_picker.dart na Web, e image_picker em IO (mobile/desktop).
import 'web_file_picker.dart'
    if (dart.library.io) 'package:image_picker/image_picker.dart';

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
    if (kIsWeb) {
      // Web: usa nosso wrapper dart:html
      final webFile = await pickWebFile(accept: ['image/*']);
      if (webFile == null) return;
      final reader = html.FileReader();
      reader.readAsArrayBuffer(webFile);
      await reader.onLoad.first;
      final bytes = reader.result as Uint8List;
      setState(() {
        _logoBytes = bytes;
        _logoName = webFile.name;
      });
    } else {
      // Mobile/Desktop: usa image_picker
      final XFile? picked = await ImagePicker().pickImage(
        source: ImageSource.gallery,
        maxWidth: 1200,
        maxHeight: 1200,
        imageQuality: 90,
      );
      if (picked == null) return;
      final bytes = await picked.readAsBytes();
      setState(() {
        _logoBytes = bytes;
        _logoName = picked.name;
      });
    }

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Logo selecionado: $_logoName')),
    );
  }

  Future<void> _enviar() async {
    if (!_formKey.currentState!.validate()) return;
    if (_logoBytes == null || _logoName == null) {
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
        _logoBytes!,
        filename: _logoName!,
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
          child: Column(
            children: [
              _buildField(_nomeCtrl, 'Nome da Empresa'),
              SizedBox(height: 16),
              _buildField(_cnpjCtrl, 'CNPJ'),
              SizedBox(height: 16),
              _buildField(_emailContatoCtrl, 'E-mail de Contato',
                  TextInputType.emailAddress),
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
                    color: Colors.transparent,
                    border: Border.all(color: Colors.grey),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  alignment: Alignment.center,
                  clipBehavior: Clip.hardEdge,
                  child: _logoBytes == null
                      ? Text('Clique para escolher o logo')
                      : Image.memory(
                          _logoBytes!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          height: double.infinity,
                        ),
                ),
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
      validator: (v) => v == null || v.trim().isEmpty ? 'Preencha este campo' : null,
    );
  }
}

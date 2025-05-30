import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class FormularioAppEmpresa extends StatefulWidget {
  final int companyId;
   const FormularioAppEmpresa({Key? key, required this.companyId}) : super(key: key);

  @override
  _FormularioAppEmpresaState createState() => _FormularioAppEmpresaState();
}

class _FormularioAppEmpresaState extends State<FormularioAppEmpresa> {
  final _formKey = GlobalKey<FormState>();
  final _corController = TextEditingController();
  final _tamanhoController = TextEditingController();
  final _companyIdController = TextEditingController();

  bool _isLoading = false;
  String? _responseMessage;

  Future<void> _enviarApp() async {
    if (!_formKey.currentState!.validate()) return;

    final companyId = _companyIdController.text.trim();
    final url = Uri.parse('http://127.0.0.1:8000/companies/$companyId/build');

    setState(() {
      _isLoading = true;
      _responseMessage = null;
    });

    try {
      final response = await http.post(url, headers: {
        'Accept': 'application/json',
      });

      if (response.statusCode == 201) {
        setState(() {
          _responseMessage = 'Build disparado com sucesso!';
        });
      } else {
        setState(() {
          _responseMessage =
              'Erro ${response.statusCode}: ${response.body}';
        });
      }
    } catch (e) {
      setState(() {
        _responseMessage = 'Falha ao conectar: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  void dispose() {
    _corController.dispose();
    _tamanhoController.dispose();
    _companyIdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Enviar App para Empresa'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextFormField(
                        controller: _corController,
                        decoration: const InputDecoration(
                          labelText: 'Cor (temporário)',
                        ),
                        validator: (v) => v == null || v.isEmpty
                            ? 'Preencha a cor'
                            : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _tamanhoController,
                        decoration: const InputDecoration(
                          labelText: 'Tamanho (temporário)',
                        ),
                        validator: (v) => v == null || v.isEmpty
                            ? 'Preencha o tamanho'
                            : null,
                      ),
                      const SizedBox(height: 12),
                      TextFormField(
                        controller: _companyIdController,
                        decoration: const InputDecoration(
                          labelText: 'Company ID',
                          hintText: 'ID da empresa para o POST',
                        ),
                        keyboardType: TextInputType.number,
                        validator: (v) => v == null ||
                                v.isEmpty ||
                                int.tryParse(v) == null
                            ? 'Informe um ID válido'
                            : null,
                      ),
                      const SizedBox(height: 24),
                      _isLoading
                          ? const CircularProgressIndicator()
                          : ElevatedButton(
                              onPressed: _enviarApp,
                              child: const Text('Enviar app'),
                            ),
                      if (_responseMessage != null) ...[
                        const SizedBox(height: 16),
                        Text(
                          _responseMessage!,
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            color: _responseMessage!
                                    .toLowerCase()
                                    .contains('sucesso')
                                ? Colors.green
                                : Colors.red,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

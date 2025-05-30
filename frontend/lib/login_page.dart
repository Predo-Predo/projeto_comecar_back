import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

// Substitua pela URL do seu backend
const String apiBaseUrl = 'http://127.0.0.1:8000';

class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _cnpjCtrl = TextEditingController();
  bool _loading = false;

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _loading = true);
    final email = _emailCtrl.text.trim();
    final cnpj  = _cnpjCtrl.text.trim();

    // Chama GET /empresas/?email_contact=...&cnpj=...
    final uri = Uri.parse('$apiBaseUrl/empresas/').replace(queryParameters: {
      'email_contact': email,
      'cnpj': cnpj,
    });
    final res = await http.get(uri);

    setState(() => _loading = false);

    if (res.statusCode == 200) {
      final List<dynamic> list = json.decode(res.body);
      if (list.isNotEmpty) {
        final company = list.first;
        final companyId = company['id'] as int;
        // Navega para o formulário de app, passando o ID
        Navigator.of(context).pushReplacementNamed(
          '/formulario_app',
          arguments: companyId,
        );
        return;
      }
    }

    // Se chegou aqui, login falhou
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Erro'),
        content: const Text('Empresa não encontrada.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _emailCtrl.dispose();
    _cnpjCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.teal[50],
      body: Center(
        child: Card(
          margin: const EdgeInsets.symmetric(horizontal: 24),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Form(
              key: _formKey,
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                const Text(
                  'Sign In',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),

                // Email
                TextFormField(
                  controller: _emailCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    prefixIcon: Icon(Icons.email_outlined),
                  ),
                  keyboardType: TextInputType.emailAddress,
                  validator: (v) => (v == null || v.isEmpty)
                      ? 'Preencha seu email'
                      : null,
                ),
                const SizedBox(height: 16),

                // CNPJ
                TextFormField(
                  controller: _cnpjCtrl,
                  decoration: const InputDecoration(
                    labelText: 'CNPJ',
                    prefixIcon: Icon(Icons.account_balance_outlined),
                  ),
                  validator: (v) => (v == null || v.isEmpty)
                      ? 'Preencha seu CNPJ'
                      : null,
                ),
                const SizedBox(height: 24),

                // Botão de login
                ElevatedButton(
                  onPressed: _loading ? null : _login,
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size.fromHeight(48),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                  child: _loading
                      ? const SizedBox(
                          width: 24, height: 24,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : const Text('Log In'),
                ),
              ]),
            ),
          ),
        ),
      ),
    );
  }
}

import 'dart:convert';
import 'dart:html' as html;
import 'dart:js' as js;

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'tela_de_produtos.dart'; // import para não quebrar nada

class LoginPage extends StatefulWidget {
  const LoginPage({Key? key}) : super(key: key);
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _emailCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  final _storage = FlutterSecureStorage();
  bool _loading = false;

  static const String BACKEND_URL = 'https://3213-177-129-251-249.ngrok-free.app';

  Future<void> _loginWithEmail() async {
    setState(() => _loading = true);

    final uri = Uri.parse('$BACKEND_URL/auth/login');
    final resp = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': _emailCtrl.text,
        'password': _passCtrl.text,
      }),
    );

    if (resp.statusCode == 200) {
      try {
        final data = jsonDecode(resp.body);
        await _storage.write(key: 'token', value: data['access_token']);
        Navigator.pushReplacementNamed(context, '/home');
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Resposta inválida do servidor: $e')),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erro (${resp.statusCode}): ${resp.body}')),
      );
    }

    setState(() => _loading = false);
  }

  Future<void> _loginWithGoogle() async {
    setState(() => _loading = true);

    void listener(html.Event event) async {
      html.CustomEvent customEvent = event as html.CustomEvent;
      final String idToken = customEvent.detail;

      final resp = await http.post(
        Uri.parse('$BACKEND_URL/auth/google/callback'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'token': idToken}),
      );

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        await _storage.write(key: 'token', value: data['access_token']);
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erro no login Google: ${resp.statusCode}')),
        );
      }

      html.window.removeEventListener('googleLogin', listener);
      setState(() => _loading = false);
    }

    html.window.addEventListener('googleLogin', listener);

    // Chama função JS segura que dispara o login Google (se disponível)
    js.context.callMethod('showGoogleLogin');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Login')),
      body: _loading
          ? Center(child: CircularProgressIndicator())
          : Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  TextField(
                    controller: _emailCtrl,
                    decoration: InputDecoration(labelText: 'E-mail'),
                  ),
                  SizedBox(height: 8),
                  TextField(
                    controller: _passCtrl,
                    decoration: InputDecoration(labelText: 'Senha'),
                    obscureText: true,
                  ),
                  SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loginWithEmail,
                    child: Text('Entrar'),
                  ),
                  SizedBox(height: 24),
                  OutlinedButton.icon(
                    icon: Image.asset('assets/google_logo.png', height: 24),
                    label: Text('Entrar com Google'),
                    onPressed: _loginWithGoogle,
                  ),
                ],
              ),
            ),
    );
  }
}

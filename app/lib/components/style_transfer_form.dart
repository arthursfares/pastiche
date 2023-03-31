import 'package:app/components/style_transfer_service.dart';
import 'package:app/components/url_text_field.dart';
import 'package:flutter/material.dart';

class StyleTransferForm extends StatefulWidget {
  const StyleTransferForm({super.key});

  @override
  State<StyleTransferForm> createState() => _StyleTransferFormState();
}

class _StyleTransferFormState extends State<StyleTransferForm> {
  final StyleTransferService _styleTransferService = StyleTransferService();
  final _formKey = GlobalKey<FormState>();
  final _contentUrlController = TextEditingController();
  final _styleUrlController = TextEditingController();
  bool _isLoading = false;
  Image? _resultImage;
  final String _placeholderAnimationUrl =
      "https://media.tenor.com/hofDex804NsAAAAj/slimer-pixel.gif";

  Future<void> _submitForm() async {
    if (_formKey.currentState!.validate()) {
      setState(() => _isLoading = true);
      final request = {
        "content": {"file_name": "content", "url": _contentUrlController.text},
        "style": {"file_name": "style", "url": _styleUrlController.text},
        "content_blending_ratio": {"value": 0.0}
      };
      try {
        final bytes = await _styleTransferService.transferStyle(request);
        final image = Image.memory(bytes);
        setState(() => _resultImage = image);
      } catch (error) {
        debugPrint(error.toString());
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final Size size = MediaQuery.of(context).size;

    return Scaffold(
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Form(
            key: _formKey,
            child: Center(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const SizedBox(height: 32),
                  SizedBox(
                    width: size.width / 3,
                    child: UrlTextField(
                      urlController: _contentUrlController,
                      labelText: 'Content image URL',
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: size.width / 3,
                    child: UrlTextField(
                      urlController: _styleUrlController,
                      labelText: 'Style image URL',
                    ),
                  ),
                  const SizedBox(height: 64),
                  SizedBox(
                    width: 100,
                    height: 100,
                    child: ElevatedButton(
                      onPressed: _isLoading ? null : _submitForm,
                      style: ElevatedButton.styleFrom(
                        shape: const CircleBorder(),
                        backgroundColor: Colors.grey[800],
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Submit'),
                    ),
                  ),
                  const SizedBox(height: 64),
                  SizedBox(
                    height: 384.0,
                    width: 384.0,
                    child: Center(
                      child: _resultImage ??
                          Image.network(_placeholderAnimationUrl),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

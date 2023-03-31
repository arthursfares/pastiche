import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class UrlTextField extends StatefulWidget {
  final TextEditingController urlController;
  final String labelText;

  const UrlTextField({
    super.key,
    required this.urlController,
    required this.labelText,
  });

  @override
  State<UrlTextField> createState() => _UrlTextFieldState();
}

class _UrlTextFieldState extends State<UrlTextField> {
  final _urlFocusNode = FocusNode();

  @override
  void dispose() {
    widget.urlController.dispose();
    _urlFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.urlController,
      focusNode: _urlFocusNode,
      decoration: InputDecoration(labelText: widget.labelText),
      keyboardType: TextInputType.url,
      textInputAction: TextInputAction.go,
      inputFormatters: [
        FilteringTextInputFormatter.deny(
          // disallow spaces and backslashes
          RegExp('[\\s\\\\]'), 
        ),
        // limit input to 200 characters
        LengthLimitingTextInputFormatter(200),
      ],
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Please enter a URL';
        }
        return null;
      },
    );
  }
}

# Pastiche
### Artistic Style Transfer API

Made based on this [tutorial](https://www.tensorflow.org/lite/examples/style_transfer/overview) 〜(￣▽￣〜)

### How to use it
Clone the repository
```
git clone https://github.com/arthursfares/pastiche.git
cd pastiche
``` 
Launch api server
```
uvicorn api.main:app --reload
```
Launch Flutter web application
```
flutter run app/lib/main.dart -d chrome
```
import 'dart:async';

import 'package:meditation_companion/features/auth/exceptions/auth_exception.dart';
import 'package:meditation_companion/features/auth/models/user_model.dart';
import 'package:meditation_companion/features/auth/repository/auth_repository.dart';

class MockAuthRepository implements AuthRepository {
  // Simulate a database of users
  final Map<String, _MockUser> _users = {
    'test@example.com': _MockUser(
      email: 'test@example.com',
      password: 'password123',
      user: User(
        id: 'test-user-id',
        email: 'test@example.com',
        emailVerifiedAt: DateTime.now(),
      ),
    ),
  };

  User? _currentUser;
  final _authStateController = StreamController<User?>.broadcast();

  static const _mockDelay = Duration(milliseconds: 1000);

  @override
  Stream<User?> get authStateChanges => _authStateController.stream;

  @override
  User? get currentUser => _currentUser;

  @override
  Future<User> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    await Future.delayed(_mockDelay);

    final mockUser = _users[email];
    if (mockUser == null) {
      throw AuthException.userNotFound();
    }

    if (mockUser.password != password) {
      throw AuthException.invalidCredentials();
    }

    _currentUser = mockUser.user;
    _authStateController.add(_currentUser);
    return _currentUser!;
  }

  @override
  Future<User> signUpWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    await Future.delayed(_mockDelay);

    if (_users.containsKey(email)) {
      throw AuthException.emailAlreadyInUse();
    }

    if (password.length < 6) {
      throw AuthException.weakPassword();
    }

    final user = User(
      id: 'user-${_users.length + 1}',
      email: email,
      createdAt: DateTime.now(),
    );

    _users[email] = _MockUser(
      email: email,
      password: password,
      user: user,
    );

    _currentUser = user;
    _authStateController.add(_currentUser);
    return user;
  }

  @override
  Future<void> sendPasswordResetEmail(String email) async {
    await Future.delayed(_mockDelay);

    if (!_users.containsKey(email)) {
      throw AuthException.userNotFound();
    }

    // In a real implementation, this would send an email.
    // Intentionally no logging here to avoid leaking the user's email.
  }

  @override
  Future<void> signOut() async {
    await Future.delayed(_mockDelay);
    _currentUser = null;
    _authStateController.add(null);
  }

  void dispose() {
    _authStateController.close();
  }
}

class _MockUser {
  final String email;
  final String password;
  final User user;

  const _MockUser({
    required this.email,
    required this.password,
    required this.user,
  });
}

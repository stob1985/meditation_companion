import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:meditation_companion/features/auth/bloc/auth_bloc.dart';
import 'package:meditation_companion/features/auth/bloc/auth_event.dart';
import 'package:meditation_companion/features/auth/bloc/auth_state.dart';
import 'package:meditation_companion/features/auth/views/login_screen.dart';
import 'package:meditation_companion/features/game/views/game_view.dart';

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        // Show loading indicator while checking auth state
        if (state is AuthInitial || state is AuthLoading) {
          return const Scaffold(
            body: Center(
              child: CircularProgressIndicator(),
            ),
          );
        }

        // Show login screen if unauthenticated
        if (state is Unauthenticated) {
          return const LoginScreen();
        }

        // Show home screen if authenticated
        if (state is Authenticated) {
          return Scaffold(
            appBar: AppBar(
              title: const Text('Meditation Companion'),
              actions: [
                IconButton(
                  icon: const Icon(Icons.logout),
                  onPressed: () {
                    context.read<AuthBloc>().add(SignOutRequested());
                  },
                ),
              ],
            ),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Welcome! You are logged in.'),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    icon: const Icon(Icons.spa),
                    label: const Text('Play Memory Match'),
                    onPressed: () =>
                        Navigator.of(context).push(GameView.route()),
                  ),
                ],
              ),
            ),
          );
        }

        // Show error state
        if (state is AuthError) {
          return Scaffold(
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    state.message,
                    style: const TextStyle(color: Colors.red),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      context.read<AuthBloc>().add(AuthCheckRequested());
                    },
                    child: const Text('Try Again'),
                  ),
                ],
              ),
            ),
          );
        }

        // Emit unauthenticated state for any unhandled states
        context.read<AuthBloc>().add(AuthCheckRequested());
        return const Scaffold(
          body: Center(
            child: CircularProgressIndicator(),
          ),
        );
      },
    );
  }
}

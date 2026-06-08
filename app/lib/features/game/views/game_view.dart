import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:meditation_companion/features/game/bloc/game_bloc.dart';
import 'package:meditation_companion/features/game/bloc/game_event.dart';
import 'package:meditation_companion/features/game/bloc/game_state.dart';
import 'package:meditation_companion/features/game/models/game_card.dart';
import 'package:meditation_companion/features/game/repository/game_repository.dart';

/// Memory match mini-game screen.
///
/// Reads its [GameBloc] from the widget tree, so it can be hosted under any
/// provider (see [GameView.route] for a ready-to-push entry point).
class GameView extends StatelessWidget {
  const GameView({super.key});

  /// Builds a route that provides a fresh [GameBloc] and starts a game.
  static Route<void> route() {
    return MaterialPageRoute<void>(
      builder: (_) => BlocProvider(
        create: (_) => GameBloc(gameRepository: GameRepository())
          ..add(const GameStarted()),
        child: const GameView(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Memory Match'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Restart',
            onPressed: () => context.read<GameBloc>().add(const GameReset()),
          ),
        ],
      ),
      body: BlocBuilder<GameBloc, GameState>(
        builder: (context, state) {
          if (state.status == GameStatus.initial) {
            return const Center(child: CircularProgressIndicator());
          }

          return Column(
            children: [
              _StatusBar(state: state),
              if (state.status == GameStatus.won)
                _WinBanner(
                  moves: state.moves,
                  onPlayAgain: () =>
                      context.read<GameBloc>().add(const GameReset()),
                ),
              Expanded(child: _Board(cards: state.cards)),
            ],
          );
        },
      ),
    );
  }
}

class _StatusBar extends StatelessWidget {
  final GameState state;

  const _StatusBar({required this.state});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('Moves: ${state.moves}',
              style: Theme.of(context).textTheme.titleMedium),
          Text('Pairs: ${state.matchedPairs}/${state.totalPairs}',
              style: Theme.of(context).textTheme.titleMedium),
        ],
      ),
    );
  }
}

class _WinBanner extends StatelessWidget {
  final int moves;
  final VoidCallback onPlayAgain;

  const _WinBanner({required this.moves, required this.onPlayAgain});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: Theme.of(context).colorScheme.primaryContainer,
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(
            '🎉 You won in $moves moves!',
            style: Theme.of(context).textTheme.titleLarge,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          ElevatedButton(
            onPressed: onPlayAgain,
            child: const Text('Play again'),
          ),
        ],
      ),
    );
  }
}

class _Board extends StatelessWidget {
  final List<GameCard> cards;

  const _Board({required this.cards});

  @override
  Widget build(BuildContext context) {
    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 4,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: cards.length,
      itemBuilder: (context, index) => _CardTile(card: cards[index]),
    );
  }
}

class _CardTile extends StatelessWidget {
  final GameCard card;

  const _CardTile({required this.card});

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final faceUp = card.isFlipped || card.isMatched;

    return GestureDetector(
      key: ValueKey('card_${card.id}'),
      onTap: faceUp
          ? null
          : () => context.read<GameBloc>().add(CardFlipped(card.id)),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        decoration: BoxDecoration(
          color: card.isMatched
              ? colorScheme.primaryContainer
              : faceUp
                  ? colorScheme.surfaceContainerHighest
                  : colorScheme.primary,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Center(
          child: Text(
            faceUp ? card.symbol : '',
            style: const TextStyle(fontSize: 32),
          ),
        ),
      ),
    );
  }
}

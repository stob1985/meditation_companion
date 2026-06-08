import 'dart:async';

import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:meditation_companion/features/game/bloc/game_event.dart';
import 'package:meditation_companion/features/game/bloc/game_state.dart';
import 'package:meditation_companion/features/game/models/game_card.dart';
import 'package:meditation_companion/features/game/repository/game_repository.dart';

/// Drives a memory match (concentration) game.
///
/// Responsibilities:
///  - building a shuffled deck via [IGameRepository] on [GameStarted]/[GameReset],
///  - flipping cards and resolving pairs on [CardFlipped],
///  - tracking moves/matched pairs and signalling a win.
class GameBloc extends Bloc<GameEvent, GameState> {
  final IGameRepository _gameRepository;

  /// How long a non-matching pair stays revealed before flipping back.
  /// Exposed for tests so they can keep the delay short/deterministic.
  final Duration mismatchDelay;

  GameBloc({
    required IGameRepository gameRepository,
    this.mismatchDelay = const Duration(milliseconds: 800),
  })  : _gameRepository = gameRepository,
        super(const GameState()) {
    on<GameStarted>(_onGameStarted);
    on<GameReset>(_onGameReset);
    on<CardFlipped>(_onCardFlipped);
  }

  void _onGameStarted(GameStarted event, Emitter<GameState> emit) {
    emit(_freshGame(event.pairCount));
  }

  void _onGameReset(GameReset event, Emitter<GameState> emit) {
    // Reshuffle while keeping the same number of pairs as the current board.
    final pairCount = state.totalPairs > 0 ? state.totalPairs : 6;
    emit(_freshGame(pairCount));
  }

  Future<void> _onCardFlipped(
    CardFlipped event,
    Emitter<GameState> emit,
  ) async {
    if (state.status != GameStatus.playing) return;

    final card = _cardById(event.cardId);
    if (card == null || card.isFlipped || card.isMatched) return;

    // Ignore taps while two cards are already face up and being resolved.
    final faceUp =
        state.cards.where((c) => c.isFlipped && !c.isMatched).toList();
    if (faceUp.length >= 2) return;

    // Reveal the tapped card.
    final revealed = _mapCards(
      state.cards,
      (c) => c.id == event.cardId ? c.copyWith(isFlipped: true) : c,
    );
    emit(state.copyWith(cards: revealed));

    final nowFaceUp =
        revealed.where((c) => c.isFlipped && !c.isMatched).toList();
    if (nowFaceUp.length < 2) return;

    // A turn is completed once the second card is revealed.
    final moves = state.moves + 1;
    final first = nowFaceUp[0];
    final second = nowFaceUp[1];

    if (first.symbol == second.symbol) {
      final matched = _mapCards(
        revealed,
        (c) => (c.id == first.id || c.id == second.id)
            ? c.copyWith(isMatched: true)
            : c,
      );
      final matchedPairs = state.matchedPairs + 1;
      final hasWon = matchedPairs == state.totalPairs;
      emit(state.copyWith(
        cards: matched,
        moves: moves,
        matchedPairs: matchedPairs,
        status: hasWon ? GameStatus.won : GameStatus.playing,
      ));
    } else {
      // Show both cards briefly, then flip them back down.
      emit(state.copyWith(cards: revealed, moves: moves));
      await Future.delayed(mismatchDelay);
      final hidden = _mapCards(
        revealed,
        (c) => (c.id == first.id || c.id == second.id)
            ? c.copyWith(isFlipped: false)
            : c,
      );
      emit(state.copyWith(cards: hidden, moves: moves));
    }
  }

  GameState _freshGame(int pairCount) {
    return GameState(
      cards: _gameRepository.generateDeck(pairCount: pairCount),
      moves: 0,
      matchedPairs: 0,
      status: GameStatus.playing,
    );
  }

  GameCard? _cardById(int id) {
    for (final c in state.cards) {
      if (c.id == id) return c;
    }
    return null;
  }

  List<GameCard> _mapCards(
    List<GameCard> cards,
    GameCard Function(GameCard) transform,
  ) {
    return cards.map(transform).toList();
  }
}

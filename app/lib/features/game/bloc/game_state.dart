import 'package:equatable/equatable.dart';

import 'package:meditation_companion/features/game/models/game_card.dart';

/// Lifecycle status of a memory match game.
enum GameStatus {
  /// No game in progress yet.
  initial,

  /// A game is being played.
  playing,

  /// All pairs have been matched.
  won,
}

/// Immutable snapshot of the memory match game.
///
/// A single state class is used (rather than one class per status) because the
/// board, move counter and status all change continuously together as the game
/// is played; [status] distinguishes the phase the UI should render.
class GameState extends Equatable {
  /// The current board, in display order.
  final List<GameCard> cards;

  /// Number of completed turns (a turn = two cards revealed).
  final int moves;

  /// Number of pairs matched so far.
  final int matchedPairs;

  /// Current lifecycle phase of the game.
  final GameStatus status;

  const GameState({
    this.cards = const [],
    this.moves = 0,
    this.matchedPairs = 0,
    this.status = GameStatus.initial,
  });

  /// Total number of pairs in the deck.
  int get totalPairs => cards.length ~/ 2;

  GameState copyWith({
    List<GameCard>? cards,
    int? moves,
    int? matchedPairs,
    GameStatus? status,
  }) {
    return GameState(
      cards: cards ?? this.cards,
      moves: moves ?? this.moves,
      matchedPairs: matchedPairs ?? this.matchedPairs,
      status: status ?? this.status,
    );
  }

  @override
  List<Object> get props => [cards, moves, matchedPairs, status];
}

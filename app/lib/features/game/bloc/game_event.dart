import 'package:equatable/equatable.dart';

abstract class GameEvent extends Equatable {
  const GameEvent();

  @override
  List<Object> get props => [];
}

/// Starts (or restarts) a game with [pairCount] pairs and a freshly
/// shuffled deck.
class GameStarted extends GameEvent {
  final int pairCount;

  const GameStarted({this.pairCount = 6});

  @override
  List<Object> get props => [pairCount];
}

/// Dispatched when the player taps a face-down card identified by [cardId].
class CardFlipped extends GameEvent {
  final int cardId;

  const CardFlipped(this.cardId);

  @override
  List<Object> get props => [cardId];
}

/// Resets the current game, reshuffling the deck.
class GameReset extends GameEvent {
  const GameReset();
}

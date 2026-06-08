import 'package:equatable/equatable.dart';

/// A single card on the memory match board.
///
/// Cards are immutable; use [copyWith] to produce updated instances when the
/// player flips a card or a matching pair is found.
class GameCard extends Equatable {
  /// Unique identifier of this card within a deck (0-based).
  final int id;

  /// The symbol printed on the card. Two cards form a pair when they share
  /// the same [symbol].
  final String symbol;

  /// Whether the card is currently face up.
  final bool isFlipped;

  /// Whether the card has already been matched with its pair.
  final bool isMatched;

  const GameCard({
    required this.id,
    required this.symbol,
    this.isFlipped = false,
    this.isMatched = false,
  });

  GameCard copyWith({
    bool? isFlipped,
    bool? isMatched,
  }) {
    return GameCard(
      id: id,
      symbol: symbol,
      isFlipped: isFlipped ?? this.isFlipped,
      isMatched: isMatched ?? this.isMatched,
    );
  }

  @override
  List<Object> get props => [id, symbol, isFlipped, isMatched];
}

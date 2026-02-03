import 'package:flutter/material.dart';
import '../models/models.dart';
import '../theme/astrokin_theme.dart';

class EventCard extends StatelessWidget {
  final AstrologicalEvent event;
  final VoidCallback? onTap;

  const EventCard({
    super.key,
    required this.event,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
        child: Padding(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(AstroKinSpacing.sm),
                    decoration: BoxDecoration(
                      color: _getImpactColor(event.impact).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                    ),
                    child: Text(
                      event.typeIcon,
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                  const SizedBox(width: AstroKinSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          event.name,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          _formatDate(event.startDate),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AstroKinTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  ),
                  _buildImpactBadge(context),
                ],
              ),
              const SizedBox(height: AstroKinSpacing.md),
              Text(
                event.description,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              if (event.tips.isNotEmpty) ...[
                const SizedBox(height: AstroKinSpacing.md),
                Text(
                  'Tip: ${event.tips.first}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AstroKinTheme.primaryBlue,
                        fontStyle: FontStyle.italic,
                      ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImpactBadge(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AstroKinSpacing.sm,
        vertical: AstroKinSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: _getImpactColor(event.impact).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AstroKinRadius.sm),
        border: Border.all(
          color: _getImpactColor(event.impact).withValues(alpha: 0.5),
        ),
      ),
      child: Text(
        event.impactEmoji,
        style: const TextStyle(fontSize: 16),
      ),
    );
  }

  Color _getImpactColor(EventImpact impact) {
    switch (impact) {
      case EventImpact.positive:
        return AstroKinTheme.energyHigh;
      case EventImpact.neutral:
        return AstroKinTheme.energyMedium;
      case EventImpact.challenging:
        return AstroKinTheme.energyLow;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = date.difference(now).inDays;

    if (difference == 0) return 'Today';
    if (difference == 1) return 'Tomorrow';
    if (difference < 7) return 'In $difference days';

    return '${date.month}/${date.day}/${date.year}';
  }
}

class CompactEventCard extends StatelessWidget {
  final AstrologicalEvent event;
  final VoidCallback? onTap;

  const CompactEventCard({
    super.key,
    required this.event,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        onTap: onTap,
        leading: Container(
          padding: const EdgeInsets.all(AstroKinSpacing.sm),
          decoration: BoxDecoration(
            color: _getImpactColor(event.impact).withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AstroKinRadius.sm),
          ),
          child: Text(
            event.typeIcon,
            style: const TextStyle(fontSize: 20),
          ),
        ),
        title: Text(
          event.name,
          style: Theme.of(context).textTheme.titleSmall,
        ),
        subtitle: Text(
          _formatDate(event.startDate),
          style: Theme.of(context).textTheme.bodySmall,
        ),
        trailing: Text(
          event.impactEmoji,
          style: const TextStyle(fontSize: 18),
        ),
      ),
    );
  }

  Color _getImpactColor(EventImpact impact) {
    switch (impact) {
      case EventImpact.positive:
        return AstroKinTheme.energyHigh;
      case EventImpact.neutral:
        return AstroKinTheme.energyMedium;
      case EventImpact.challenging:
        return AstroKinTheme.energyLow;
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = date.difference(now).inDays;

    if (difference == 0) return 'Today';
    if (difference == 1) return 'Tomorrow';
    if (difference < 7) return 'In $difference days';

    return '${date.month}/${date.day}';
  }
}

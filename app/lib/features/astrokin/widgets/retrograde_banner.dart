import 'package:flutter/material.dart';
import '../models/models.dart';
import '../theme/astrokin_theme.dart';

class RetrogradeBanner extends StatelessWidget {
  final RetrogradeInfo retrograde;
  final VoidCallback? onTap;

  const RetrogradeBanner({
    super.key,
    required this.retrograde,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: AstroKinSpacing.md),
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              AstroKinTheme.primaryPurple.withValues(alpha: 0.8),
              AstroKinTheme.primaryBlue.withValues(alpha: 0.8),
            ],
          ),
          borderRadius: BorderRadius.circular(AstroKinRadius.lg),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(AstroKinSpacing.sm),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(AstroKinRadius.sm),
              ),
              child: Text(
                retrograde.planetSymbol,
                style: const TextStyle(fontSize: 24, color: Colors.white),
              ),
            ),
            const SizedBox(width: AstroKinSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${retrograde.planetName} Retrograde Active',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${retrograde.daysRemaining} days remaining',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.white.withValues(alpha: 0.8),
                        ),
                  ),
                ],
              ),
            ),
            Icon(
              Icons.arrow_forward_ios,
              color: Colors.white.withValues(alpha: 0.8),
              size: 16,
            ),
          ],
        ),
      ),
    );
  }
}

class RetrogradeProgressCard extends StatelessWidget {
  final RetrogradeInfo retrograde;
  final VoidCallback? onTap;

  const RetrogradeProgressCard({
    super.key,
    required this.retrograde,
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
                  Text(
                    retrograde.planetSymbol,
                    style: const TextStyle(fontSize: 32),
                  ),
                  const SizedBox(width: AstroKinSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '${retrograde.planetName} Retrograde',
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        Text(
                          retrograde.affectedArea,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: AstroKinTheme.textSecondary,
                              ),
                        ),
                      ],
                    ),
                  ),
                  _buildStatusBadge(context),
                ],
              ),
              const SizedBox(height: AstroKinSpacing.md),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: retrograde.progress,
                  backgroundColor: Colors.grey.shade200,
                  valueColor: AlwaysStoppedAnimation(
                    retrograde.isActive
                        ? AstroKinTheme.primaryPurple
                        : AstroKinTheme.textSecondary,
                  ),
                  minHeight: 8,
                ),
              ),
              const SizedBox(height: AstroKinSpacing.sm),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _formatDate(retrograde.startDate),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  Text(
                    retrograde.isActive
                        ? '${retrograde.daysRemaining} days left'
                        : retrograde.isUpcoming
                            ? 'Starts in ${retrograde.daysUntilStart} days'
                            : 'Completed',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: AstroKinTheme.primaryPurple,
                        ),
                  ),
                  Text(
                    _formatDate(retrograde.endDate),
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(BuildContext context) {
    final isActive = retrograde.isActive;
    final isUpcoming = retrograde.isUpcoming;

    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AstroKinSpacing.sm,
        vertical: AstroKinSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: isActive
            ? AstroKinTheme.energyLow.withValues(alpha: 0.1)
            : isUpcoming
                ? AstroKinTheme.energyMedium.withValues(alpha: 0.1)
                : AstroKinTheme.energyHigh.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AstroKinRadius.sm),
      ),
      child: Text(
        isActive ? 'Active' : isUpcoming ? 'Upcoming' : 'Passed',
        style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: isActive
                  ? AstroKinTheme.energyLow
                  : isUpcoming
                      ? AstroKinTheme.energyMedium
                      : AstroKinTheme.energyHigh,
              fontWeight: FontWeight.bold,
            ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.month}/${date.day}';
  }
}

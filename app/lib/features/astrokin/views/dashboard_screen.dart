import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../widgets/widgets.dart';
import '../theme/astrokin_theme.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        if (state.isLoading && state.family == null) {
          return const Center(child: CircularProgressIndicator());
        }

        return RefreshIndicator(
          onRefresh: () async {
            context.read<AstroKinBloc>().add(RefreshDashboard());
          },
          child: SingleChildScrollView(
            physics: const AlwaysScrollableScrollPhysics(),
            padding: const EdgeInsets.all(AstroKinSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Active Retrograde Banner
                if (state.isRetrogradActive && state.activeRetrogrades.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: AstroKinSpacing.md),
                    child: RetrogradeBanner(
                      retrograde: state.activeRetrogrades.first,
                      onTap: () => _navigateToRetrograde(context),
                    ),
                  ),

                // Family Energy Section
                _buildEnergySection(context, state),

                const SizedBox(height: AstroKinSpacing.lg),

                // Today's Insights
                _buildInsightsSection(context, state),

                const SizedBox(height: AstroKinSpacing.lg),

                // Upcoming Events
                _buildEventsSection(context, state),

                const SizedBox(height: AstroKinSpacing.lg),

                // Quick Actions
                _buildQuickActionsSection(context, state),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildEnergySection(BuildContext context, AstroKinState state) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Family Energy Today',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Row(
              children: [
                EnergyGauge(
                  energy: state.currentEnergy,
                  size: 120,
                ),
                const SizedBox(width: AstroKinSpacing.lg),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (state.currentEnergy?.categoryBreakdown.isNotEmpty ?? false)
                        CategoryEnergyGrid(
                          categories: state.currentEnergy!.categoryBreakdown,
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInsightsSection(BuildContext context, AstroKinState state) {
    final insights = state.currentEnergy?.insights ?? [];
    final recommendations = state.currentEnergy?.recommendations ?? [];

    if (insights.isEmpty && recommendations.isEmpty) {
      return const SizedBox.shrink();
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Today\'s Insights',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.md),
            ...insights.map((insight) => _buildInsightItem(context, insight, Icons.lightbulb_outline)),
            if (recommendations.isNotEmpty) ...[
              const Divider(height: AstroKinSpacing.lg),
              Text(
                'Recommendations',
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: AstroKinTheme.primaryBlue,
                    ),
              ),
              const SizedBox(height: AstroKinSpacing.sm),
              ...recommendations.map((rec) => _buildInsightItem(context, rec, Icons.check_circle_outline)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInsightItem(BuildContext context, String text, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(
            icon,
            size: 18,
            color: AstroKinTheme.primaryBlue,
          ),
          const SizedBox(width: AstroKinSpacing.sm),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEventsSection(BuildContext context, AstroKinState state) {
    final events = state.upcomingEvents;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Upcoming Cosmic Events',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            TextButton(
              onPressed: () => _navigateToCalendar(context),
              child: const Text('See All'),
            ),
          ],
        ),
        const SizedBox(height: AstroKinSpacing.sm),
        if (events.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(AstroKinSpacing.lg),
              child: Center(
                child: Text(
                  'No upcoming events in the next week',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AstroKinTheme.textSecondary,
                      ),
                ),
              ),
            ),
          )
        else
          ...events.take(3).map((event) => Padding(
                padding: const EdgeInsets.only(bottom: AstroKinSpacing.sm),
                child: CompactEventCard(event: event),
              )),
      ],
    );
  }

  Widget _buildQuickActionsSection(BuildContext context, AstroKinState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: AstroKinSpacing.md),
        Row(
          children: [
            Expanded(
              child: _buildQuickActionButton(
                context,
                icon: Icons.auto_awesome,
                label: 'Parenting Tips',
                color: AstroKinTheme.accentGold,
                onTap: () => _navigateToParentingHacks(context),
              ),
            ),
            const SizedBox(width: AstroKinSpacing.md),
            Expanded(
              child: _buildQuickActionButton(
                context,
                icon: Icons.people_outline,
                label: 'Sibling Guide',
                color: AstroKinTheme.primaryGreen,
                onTap: () => _navigateToSiblings(context),
              ),
            ),
          ],
        ),
        const SizedBox(height: AstroKinSpacing.md),
        Row(
          children: [
            Expanded(
              child: _buildQuickActionButton(
                context,
                icon: Icons.calendar_month,
                label: 'Peace Calendar',
                color: AstroKinTheme.primaryBlue,
                onTap: () => _navigateToCalendar(context),
              ),
            ),
            const SizedBox(width: AstroKinSpacing.md),
            Expanded(
              child: _buildQuickActionButton(
                context,
                icon: Icons.shield_outlined,
                label: 'Retrograde Kit',
                color: AstroKinTheme.primaryPurple,
                onTap: () => _navigateToRetrograde(context),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickActionButton(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
        child: Padding(
          padding: const EdgeInsets.all(AstroKinSpacing.md),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(AstroKinSpacing.md),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  icon,
                  color: color,
                  size: 28,
                ),
              ),
              const SizedBox(height: AstroKinSpacing.sm),
              Text(
                label,
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _navigateToParentingHacks(BuildContext context) {
    // Navigation handled by parent
  }

  void _navigateToSiblings(BuildContext context) {
    // Navigation handled by parent
  }

  void _navigateToCalendar(BuildContext context) {
    // Navigation handled by parent
  }

  void _navigateToRetrograde(BuildContext context) {
    // Navigation handled by parent
  }
}

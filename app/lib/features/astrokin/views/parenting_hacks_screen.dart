import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/astrokin_bloc.dart';
import '../bloc/astrokin_event.dart';
import '../bloc/astrokin_state.dart';
import '../models/models.dart';
import '../widgets/widgets.dart';
import '../theme/astrokin_theme.dart';

class ParentingHacksScreen extends StatefulWidget {
  const ParentingHacksScreen({super.key});

  @override
  State<ParentingHacksScreen> createState() => _ParentingHacksScreenState();
}

class _ParentingHacksScreenState extends State<ParentingHacksScreen> {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AstroKinBloc, AstroKinState>(
      builder: (context, state) {
        if (!state.hasChildren) {
          return _buildNoChildrenView(context);
        }

        return Column(
          children: [
            // Child Selector
            _buildChildSelector(context, state),

            // Content
            Expanded(
              child: state.selectedChild == null
                  ? _buildSelectChildPrompt(context)
                  : _buildHacksContent(context, state),
            ),
          ],
        );
      },
    );
  }

  Widget _buildChildSelector(BuildContext context, AstroKinState state) {
    return Container(
      padding: const EdgeInsets.all(AstroKinSpacing.md),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: state.children.map((child) {
            return Padding(
              padding: const EdgeInsets.only(right: AstroKinSpacing.sm),
              child: CompactMemberChip(
                member: child,
                isSelected: state.selectedChild?.id == child.id,
                onTap: () {
                  context.read<AstroKinBloc>().add(SelectChild(child));
                  context.read<AstroKinBloc>().add(LoadParentingHacks(child));
                  context.read<AstroKinBloc>().add(LoadDailyHack(child));
                },
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildNoChildrenView(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.child_care,
              size: 80,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: AstroKinSpacing.lg),
            Text(
              'No Children Added',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            Text(
              'Add your children to the family profile to get personalized parenting tips based on their zodiac signs.',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
            const SizedBox(height: AstroKinSpacing.lg),
            ElevatedButton.icon(
              onPressed: () {
                // Navigate to family profile
              },
              icon: const Icon(Icons.add),
              label: const Text('Add Child'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSelectChildPrompt(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.xl),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.touch_app,
              size: 60,
              color: Colors.grey.shade400,
            ),
            const SizedBox(height: AstroKinSpacing.md),
            Text(
              'Select a Child',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: AstroKinSpacing.sm),
            Text(
              'Tap on a child above to see personalized parenting tips',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AstroKinTheme.textSecondary,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHacksContent(BuildContext context, AstroKinState state) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AstroKinSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Child Overview Card
          _buildChildOverviewCard(context, state.selectedChild!),

          const SizedBox(height: AstroKinSpacing.lg),

          // Daily Hack
          if (state.dailyHack != null) ...[
            _buildDailyHackCard(context, state.dailyHack!),
            const SizedBox(height: AstroKinSpacing.lg),
          ],

          // All Hacks
          Text(
            'Parenting Tips for ${state.selectedChild!.zodiacSign.name}',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: AstroKinSpacing.md),
          ...state.parentingHacks.map((hack) => Padding(
                padding: const EdgeInsets.only(bottom: AstroKinSpacing.md),
                child: _buildHackCard(context, hack),
              )),
        ],
      ),
    );
  }

  Widget _buildChildOverviewCard(BuildContext context, FamilyMember child) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(AstroKinSpacing.md),
        child: Row(
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AstroKinTheme.getZodiacColor(child.zodiacSign.element.name),
                    AstroKinTheme.getZodiacColor(child.zodiacSign.element.name).withValues(alpha: 0.5),
                  ],
                ),
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  child.zodiacSign.symbol,
                  style: const TextStyle(fontSize: 32, color: Colors.white),
                ),
              ),
            ),
            const SizedBox(width: AstroKinSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    child.name,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  Text(
                    '${child.zodiacSign.name} ${child.zodiacSign.elementEmoji}',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  Text(
                    '${child.age} years old - ${child.zodiacSign.element.name.toUpperCase()} sign',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AstroKinTheme.textSecondary,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDailyHackCard(BuildContext context, ParentingHack hack) {
    return Container(
      decoration: BoxDecoration(
        gradient: AstroKinTheme.primaryGradient,
        borderRadius: BorderRadius.circular(AstroKinRadius.lg),
      ),
      padding: const EdgeInsets.all(AstroKinSpacing.md),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(AstroKinSpacing.sm),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                ),
                child: const Icon(
                  Icons.auto_awesome,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: AstroKinSpacing.sm),
              Text(
                'Today\'s Tip',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
              ),
            ],
          ),
          const SizedBox(height: AstroKinSpacing.md),
          Text(
            hack.title,
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: AstroKinSpacing.sm),
          Text(
            hack.description,
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white.withValues(alpha: 0.9),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildHackCard(BuildContext context, ParentingHack hack) {
    return Card(
      child: ExpansionTile(
        leading: Container(
          padding: const EdgeInsets.all(AstroKinSpacing.sm),
          decoration: BoxDecoration(
            color: AstroKinTheme.primaryBlue.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AstroKinRadius.sm),
          ),
          child: Text(
            hack.categoryIcon,
            style: const TextStyle(fontSize: 24),
          ),
        ),
        title: Text(
          hack.title,
          style: Theme.of(context).textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        subtitle: Text(
          hack.categoryDisplayName,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AstroKinTheme.textSecondary,
              ),
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(AstroKinSpacing.md),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  hack.description,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                if (hack.explanation != null) ...[
                  const SizedBox(height: AstroKinSpacing.md),
                  Container(
                    padding: const EdgeInsets.all(AstroKinSpacing.md),
                    decoration: BoxDecoration(
                      color: AstroKinTheme.primaryBlue.withValues(alpha: 0.05),
                      borderRadius: BorderRadius.circular(AstroKinRadius.sm),
                    ),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(
                          Icons.info_outline,
                          size: 18,
                          color: AstroKinTheme.primaryBlue,
                        ),
                        const SizedBox(width: AstroKinSpacing.sm),
                        Expanded(
                          child: Text(
                            hack.explanation!,
                            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                  fontStyle: FontStyle.italic,
                                ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                if (hack.actionItems.isNotEmpty) ...[
                  const SizedBox(height: AstroKinSpacing.md),
                  Text(
                    'Action Items:',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: AstroKinSpacing.sm),
                  ...hack.actionItems.map((item) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(
                              Icons.check_circle,
                              size: 16,
                              color: AstroKinTheme.energyHigh,
                            ),
                            const SizedBox(width: AstroKinSpacing.sm),
                            Expanded(child: Text(item)),
                          ],
                        ),
                      )),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

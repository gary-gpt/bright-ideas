<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { 
    ideaActions, 
    refinementActions, 
    planActions,
    currentIdea,
    currentRefinementSession,
    refinementProgress,
    refinementLoading,
    planLoading
  } from '$lib/stores';
  import { toastActions } from '$lib/stores';
  import Button from '$lib/components/shared/Button.svelte';
  import LoadingSpinner from '$lib/components/shared/LoadingSpinner.svelte';
  import type { IdeaDetail, RefinementSession, RefinementQuestion } from '$lib/types';

  let idea: IdeaDetail | null = null;
  let session: RefinementSession | null = null;
  let answers: Record<string, string> = {};
  let previousSessions: RefinementSession[] = [];
  let loading = true;
  let submitting = false;
  let generating = false;

  $: ideaId = $page.params.id;
  $: progress = $refinementProgress;
  $: isSubmitting = $refinementLoading || submitting;
  $: isGenerating = $planLoading || generating;

  onMount(async () => {
    if (ideaId) {
      try {
        // Load the idea first
        idea = await ideaActions.loadIdea(ideaId);
        
        // Load all sessions for this idea
        const sessions = await refinementActions.loadIdeaSessions(ideaId);
        const incompleteSession = sessions.find(s => !s.is_complete);
        const completedSessions = sessions.filter(s => s.is_complete);
        
        // Store previous sessions for context display
        previousSessions = completedSessions;
        
        if (incompleteSession) {
          // Use existing incomplete session
          session = incompleteSession;
          answers = { ...incompleteSession.answers };
          currentRefinementSession.set(session);
        } else {
          // Create a new refinement session
          session = await refinementActions.createSession(ideaId);
          answers = {};
        }
      } catch (error) {
        console.error('Failed to load idea or create refinement session:', error);
        toastActions.error('Failed to start refinement session');
        goto(`/ideas/${ideaId}`);
      } finally {
        loading = false;
      }
    }
  });

  async function handleAnswerChange(questionId: string, answer: string) {
    answers[questionId] = answer;
    
    // Auto-save answers as user types (debounced)
    if (session) {
      try {
        await refinementActions.submitAnswers(session.id, answers);
        session = $currentRefinementSession;
      } catch (error) {
        console.error('Failed to save answer:', error);
        // Don't show error for auto-save failures
      }
    }
  }

  async function submitAllAnswers() {
    if (!session) return;
    
    submitting = true;
    try {
      const updatedSession = await refinementActions.submitAnswers(session.id, answers);
      session = updatedSession;
      
      if (updatedSession.is_complete) {
        toastActions.success('Refinement session completed! You can now generate an implementation plan.');
        // Refresh the idea to show updated status
        if (idea) {
          idea = await ideaActions.loadIdea(idea.id);
        }
      } else {
        toastActions.success('Progress saved!');
      }
    } catch (error) {
      console.error('Failed to submit answers:', error);
      toastActions.error('Failed to save answers. Please try again.');
    } finally {
      submitting = false;
    }
  }

  async function generatePlan() {
    if (!session || !session.is_complete) return;
    
    generating = true;
    try {
      const plan = await planActions.generatePlan(session.id);
      toastActions.success('Implementation plan generated successfully!');
      
      // Navigate to the plan view
      goto(`/ideas/${ideaId}/plans/${plan.id}`);
    } catch (error) {
      console.error('Failed to generate plan:', error);
      toastActions.error('Failed to generate plan. Please try again.');
    } finally {
      generating = false;
    }
  }

  function getQuestionProgress(questionId: string): 'unanswered' | 'partial' | 'complete' {
    const answer = answers[questionId];
    if (!answer || answer.trim().length === 0) return 'unanswered';
    if (answer.trim().length < 20) return 'partial';
    return 'complete';
  }

  function getProgressColor(status: string): string {
    switch (status) {
      case 'complete': return 'text-green-600';
      case 'partial': return 'text-yellow-600';
      default: return 'text-gray-400';
    }
  }

  function getProgressIcon(status: string): string {
    switch (status) {
      case 'complete': return '✓';
      case 'partial': return '○';
      default: return '○';
    }
  }

  $: allQuestionsAnswered = session?.questions.every(q => 
    answers[q.id] && answers[q.id].trim().length > 0
  ) || false;

  $: canGeneratePlan = session?.is_complete && allQuestionsAnswered;
</script>

<svelte:head>
  <title>Refine: {idea ? idea.title : 'Loading...'} - Bright Ideas</title>
</svelte:head>

<div class="min-h-screen bg-secondary-50">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-4">
          <Button variant="ghost" href="/ideas/{ideaId}" size="sm">
            ← Back to Idea
          </Button>
          <div>
            <h1 class="text-2xl font-bold text-secondary-900">
              AI-Powered Refinement
            </h1>
            {#if idea}
              <p class="text-secondary-600">{idea.title}</p>
            {/if}
          </div>
        </div>
        
        <!-- Progress Indicator -->
        {#if session}
          <div class="text-right">
            <div class="text-sm text-secondary-600">Progress</div>
            <div class="text-lg font-semibold text-secondary-900">
              {progress.current} of {progress.total}
            </div>
            <div class="text-xs text-secondary-500">{progress.percentage}% complete</div>
          </div>
        {/if}
      </div>
    </div>

    {#if loading}
      <div class="flex justify-center py-12">
        <LoadingSpinner size="lg" message="Loading refinement session..." />
      </div>
    {:else if idea && session}
      <!-- Progress Bar -->
      <div class="bg-white rounded-lg shadow-sm border border-secondary-200 p-4 mb-6">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-secondary-700">Refinement Progress</span>
          <span class="text-sm text-secondary-500">{progress.percentage}%</span>
        </div>
        <div class="w-full bg-secondary-200 rounded-full h-2">
          <div 
            class="bg-primary-600 h-2 rounded-full transition-all duration-500" 
            style="width: {progress.percentage}%"
          ></div>
        </div>
        <div class="mt-2 text-xs text-secondary-500">
          Answer all questions to generate an implementation plan
        </div>
      </div>

      <!-- Previous Context (if this is a continuation) -->
      {#if previousSessions.length > 0 || (idea && idea.active_plan)}
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 class="text-lg font-semibold text-blue-900 mb-4">
            🏗️ Building on Your Previous Work
          </h3>
          <p class="text-blue-800 mb-4">
            This refinement session will build on what you've already explored. Here's what we're working with:
          </p>
          
          {#if idea && idea.active_plan}
            <div class="mb-4">
              <h4 class="font-medium text-blue-900 mb-2">Current Implementation Plan:</h4>
              <div class="bg-white rounded border border-blue-200 p-3">
                <p class="text-sm text-blue-800">{idea.active_plan.summary}</p>
                {#if idea.active_plan.steps && idea.active_plan.steps.length > 0}
                  <div class="mt-2">
                    <p class="text-xs font-medium text-blue-700 mb-1">Key Steps:</p>
                    <ul class="text-xs text-blue-600 space-y-1">
                      {#each idea.active_plan.steps.slice(0, 3) as step}
                        <li>• {step.title}</li>
                      {/each}
                      {#if idea.active_plan.steps.length > 3}
                        <li class="text-blue-500">• ... and {idea.active_plan.steps.length - 3} more steps</li>
                      {/if}
                    </ul>
                  </div>
                {/if}
              </div>
            </div>
          {/if}
          
          {#if previousSessions.length > 0}
            <div class="mb-4">
              <h4 class="font-medium text-blue-900 mb-2">Previous Refinement Sessions:</h4>
              <div class="space-y-2">
                {#each previousSessions.slice(0, 2) as prevSession, index}
                  <details class="bg-white rounded border border-blue-200">
                    <summary class="p-3 cursor-pointer text-sm font-medium text-blue-800 hover:bg-blue-50">
                      Session {previousSessions.length - index} - {new Date(prevSession.created_at).toLocaleDateString()}
                    </summary>
                    <div class="px-3 pb-3">
                      {#if prevSession.questions && prevSession.answers}
                        <div class="space-y-2">
                          {#each prevSession.questions.slice(0, 2) as question}
                            <div class="text-xs">
                              <p class="font-medium text-blue-700">Q: {question.question}</p>
                              <p class="text-blue-600 mt-1">A: {prevSession.answers[question.id] || 'No answer'}</p>
                            </div>
                          {/each}
                          {#if prevSession.questions.length > 2}
                            <p class="text-xs text-blue-500">... and {prevSession.questions.length - 2} more questions</p>
                          {/if}
                        </div>
                      {/if}
                    </div>
                  </details>
                {/each}
              </div>
            </div>
          {/if}
          
          <div class="text-sm text-blue-700 bg-blue-100 rounded-md p-3">
            💡 The questions below are designed to build on this foundation and explore new dimensions or address gaps in your current approach.
          </div>
        </div>
      {/if}

      <!-- Questions Form -->
      <div class="space-y-6">
        {#each session.questions as question, index}
          <div class="bg-white rounded-lg shadow-sm border border-secondary-200">
            <div class="p-6">
              <!-- Question Header -->
              <div class="flex items-start space-x-3 mb-4">
                <div class="flex-shrink-0 w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-primary-600">{index + 1}</span>
                </div>
                <div class="flex-1">
                  <h3 class="text-lg font-medium text-secondary-900 mb-2">
                    {question.question}
                  </h3>
                  
                  <!-- Answer Input -->
                  <div class="space-y-2">
                    <textarea
                      bind:value={answers[question.id]}
                      on:input={(e) => handleAnswerChange(question.id, e.currentTarget.value)}
                      placeholder="Share your thoughts in detail... (minimum 20 characters for meaningful refinement)"
                      class="w-full px-3 py-3 border border-secondary-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none text-secondary-900 placeholder-secondary-400"
                      rows="4"
                      disabled={isSubmitting}
                    ></textarea>
                    
                    <!-- Answer Status -->
                    <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-2">
                        <span class="text-lg {getProgressColor(getQuestionProgress(question.id))}">
                          {getProgressIcon(getQuestionProgress(question.id))}
                        </span>
                        <span class="text-sm text-secondary-600">
                          {#if getQuestionProgress(question.id) === 'complete'}
                            Complete
                          {:else if getQuestionProgress(question.id) === 'partial'}
                            Add more detail
                          {:else}
                            Not answered
                          {/if}
                        </span>
                      </div>
                      <div class="text-xs text-secondary-400">
                        {answers[question.id]?.length || 0} characters
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>

      <!-- Action Buttons -->
      <div class="mt-8 bg-white rounded-lg shadow-sm border border-secondary-200 p-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-medium text-secondary-900 mb-1">Ready for the next step?</h3>
            <p class="text-sm text-secondary-600">
              {#if !allQuestionsAnswered}
                Complete all questions to generate your implementation plan
              {:else if !session.is_complete}
                Save your answers and generate an implementation plan
              {:else}
                All questions completed! Generate your implementation plan
              {/if}
            </p>
          </div>
          
          <div class="flex space-x-3">
            {#if !session.is_complete}
              <Button 
                on:click={submitAllAnswers} 
                disabled={!allQuestionsAnswered || isSubmitting}
                loading={isSubmitting}
              >
                Save Answers
              </Button>
            {/if}
            
            {#if canGeneratePlan}
              <Button 
                on:click={generatePlan}
                disabled={isGenerating}
                loading={isGenerating}
                variant="primary"
              >
                Generate Implementation Plan
              </Button>
            {/if}
          </div>
        </div>
      </div>

      <!-- Session Info -->
      <div class="mt-6 bg-secondary-100 rounded-lg p-4">
        <div class="flex items-center justify-between text-sm">
          <div class="text-secondary-600">
            Session created: {new Date(session.created_at).toLocaleString()}
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-secondary-600">
              Status: <span class="font-medium {session.is_complete ? 'text-green-600' : 'text-yellow-600'}">
                {session.is_complete ? 'Complete' : 'In Progress'}
              </span>
            </span>
            {#if session.completed_at}
              <span class="text-secondary-600">
                Completed: {new Date(session.completed_at).toLocaleString()}
              </span>
            {/if}
          </div>
        </div>
      </div>
    {:else}
      <div class="text-center py-12">
        <h2 class="text-xl font-bold text-secondary-900 mb-2">Unable to Start Refinement</h2>
        <p class="text-secondary-600 mb-4">There was an issue loading the refinement session.</p>
        <Button href="/ideas/{ideaId}">Back to Idea</Button>
      </div>
    {/if}
  </div>
</div>
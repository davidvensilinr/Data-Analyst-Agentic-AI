'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ArrowRight, BarChart3, Zap, Shield, Lightbulb } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      {/* Navigation */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-black dark:text-white">
            DataAnalyst<span className="text-red-600"> AI</span>
          </div>
          <Link href="/projects">
            <Button variant="outline" className="border-red-600 text-red-600 hover:bg-red-50 dark:hover:bg-red-950">Sign In</Button>
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center space-y-8">
          <h1 className="text-5xl md:text-6xl font-bold text-black dark:text-white tracking-tight">
            AI-Powered Data Analysis
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto leading-relaxed">
            Upload your datasets, clean messy data, and get intelligent insights—all powered by
            autonomous agents that show you exactly how they work.
          </p>

          <div className="flex gap-4 justify-center flex-wrap">
            <Link href="/projects">
              <Button size="lg" className="bg-red-600 hover:bg-red-700 text-white">
                Get Started <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-gray-300 text-black dark:text-white dark:border-gray-600">
              Learn More
            </Button>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-20 grid md:grid-cols-4 gap-6">
          <Card className="p-6 border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-900 transition-colors">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-red-50 dark:bg-red-950 mb-4">
              <BarChart3 className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="font-semibold text-black dark:text-white mb-2">Smart Profiling</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Automatic data quality analysis with column statistics, correlations, and risk detection.
            </p>
          </Card>

          <Card className="p-6 border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-900 transition-colors">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-red-50 dark:bg-red-950 mb-4">
              <Zap className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="font-semibold text-black dark:text-white mb-2">Intelligent Cleaning</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Auto-detect and apply data transformations with before/after previews and audit trails.
            </p>
          </Card>

          <Card className="p-6 border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-900 transition-colors">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-red-50 dark:bg-red-950 mb-4">
              <Lightbulb className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="font-semibold text-black dark:text-white mb-2">Agent Insights</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Ask natural language questions and watch AI agents work step-by-step with full transparency.
            </p>
          </Card>

          <Card className="p-6 border border-gray-200 dark:border-gray-800 hover:border-red-300 dark:hover:border-red-900 transition-colors">
            <div className="flex items-center justify-center h-12 w-12 rounded-lg bg-red-50 dark:bg-red-950 mb-4">
              <Shield className="h-6 w-6 text-red-600" />
            </div>
            <h3 className="font-semibold text-black dark:text-white mb-2">Audit & Trust</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Immutable audit logs of every decision with prompts, tool calls, and model outputs.
            </p>
          </Card>
        </div>

        {/* CTA Section */}
        <div className="mt-20 bg-black dark:bg-gray-950 rounded-xl p-12 text-center border border-gray-800">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to transform your data?
          </h2>
          <p className="text-gray-300 mb-8 text-lg">
            Start analyzing in seconds. No setup required—just upload your dataset.
          </p>
          <Link href="/projects">
            <Button size="lg" className="bg-red-600 hover:bg-red-700 text-white">
              Launch App <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-slate-900 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h4 className="font-semibold text-black dark:text-white mb-4">Product</h4>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Features</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Pricing</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Security</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-black dark:text-white mb-4">Company</h4>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">About</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Blog</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Careers</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-black dark:text-white mb-4">Resources</h4>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Docs</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">API</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Support</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-black dark:text-white mb-4">Legal</h4>
              <ul className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Privacy</Link></li>
                <li><Link href="#" className="hover:text-red-600 dark:hover:text-red-400">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800">
            <p className="text-gray-600 dark:text-gray-400 text-sm text-center">
              © 2024 DataAnalyst AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}


import React from 'react';
import { motion } from 'framer-motion';

const Skeleton = ({ className }) => (
  <div className={`bg-foreground/20 overflow-hidden relative rounded-lg ${className}`}>
    <motion.div
      initial={{ x: '-100%' }}
      animate={{ x: '100%' }}
      transition={{ 
        repeat: Infinity, 
        duration: 1.5, 
        ease: "linear" 
      }}
      className="absolute inset-0 bg-gradient-to-r from-transparent via-foreground/5 to-transparent w-full h-full"
    />
  </div>
);

export const DashboardSkeleton = () => (
  <div className="space-y-8 animate-pulse">
    {/* Hero Area */}
    <Skeleton className="h-64 w-full opacity-80 dark:opacity-50" />
    
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
      <div className="lg:col-span-8 space-y-6">
        <Skeleton className="h-[500px] w-full" />
        <Skeleton className="h-40 w-full" />
      </div>
      <div className="lg:col-span-4 space-y-6">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-96 w-full" />
      </div>
    </div>
  </div>
);

export const CardSkeleton = () => (
  <div className="terminal-card bg-bg1/20 border-border p-6 space-y-4">
    <div className="flex justify-between">
      <Skeleton className="h-4 w-32" />
      <Skeleton className="h-4 w-4" />
    </div>
    <div className="space-y-2">
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
      <Skeleton className="h-10 w-full" />
    </div>
  </div>
);

export const GridSkeleton = ({ count = 4 }) => (
  <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6 animate-pulse">
    {[...Array(count)].map((_, i) => (
      <Skeleton key={i} className="h-24 w-full" />
    ))}
  </div>
);

export const DetailSkeleton = () => (
  <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-pulse">
    <div className="lg:col-span-8">
      <Skeleton className="h-[400px] w-full" />
    </div>
    <div className="lg:col-span-4 space-y-6">
      <Skeleton className="h-64 w-full" />
      <Skeleton className="h-48 w-full" />
    </div>
  </div>
);

export default Skeleton;
